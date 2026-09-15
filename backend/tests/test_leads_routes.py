import hashlib
import hmac
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import selectinload

from backend.config import Settings, get_settings
from backend.database import Base, get_db
from backend.domains.leads.models import (
    AcademicCourse,
    AcademicCourseAlias,
    CatalogStatus,
    EducationalInstitution,
    EducationalInstitutionAlias,
    InterestArea,
    Lead,
    LeadInterestArea,
    LeadType,
)
from backend.domains.usuarios.models import User
from backend.infra.limiter import limiter
from backend.main import create_app


@pytest_asyncio.fixture
async def lead_client():
    limiter.reset()
    settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        JWT_SECRET="test-jwt-secret-key-minimum-32-chars-long!",
    )
    engine = create_async_engine(settings.async_database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    app = create_app()

    async def override_get_db():
        async with factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.lead_session_factory = factory
        yield client
    await engine.dispose()


def lead_payload() -> dict:
    return {
        "full_name": "Grace Hopper",
        "email": "grace@example.com",
        "company_name": "Compilers Inc.",
        "company_size": "51-200",
        "privacy_consent": True,
    }


@pytest.mark.asyncio
async def test_public_lead_submission_and_page_view(lead_client: AsyncClient):
    trace = await lead_client.get("/health", headers={"X-Request-ID": "trace-test-1"})
    assert trace.headers["X-Request-ID"] == "trace-test-1"

    metrics = await lead_client.get("/metrics")
    assert metrics.status_code == 200
    assert b"http_requests_total" in metrics.content

    view_headers = {"Idempotency-Key": "view-request-1"}
    first_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    duplicate_view = await lead_client.post(
        "/api/v1/public/leads/views?o=instagram", headers=view_headers
    )
    assert first_view.status_code == 204
    assert duplicate_view.status_code == 204

    response = await lead_client.post("/api/v1/public/leads?o=linkedin", json=lead_payload())
    assert response.status_code == 201
    assert set(response.json()) == {"id", "created_at"}

    unauthorized = await lead_client.get("/api/v1/leads")
    assert unauthorized.status_code == 401


@pytest.mark.asyncio
async def test_public_lead_submission_is_rate_limited(lead_client: AsyncClient):
    responses = []
    for index in range(6):
        payload = lead_payload()
        payload["email"] = f"rate-{index}@example.com"
        responses.append(await lead_client.post("/api/v1/public/leads", json=payload))

    assert [response.status_code for response in responses[:5]] == [201] * 5
    assert responses[5].status_code == 429

    forged_visitor = await lead_client.post(
        "/api/v1/public/leads",
        headers={"X-Client-IP": "203.0.113.10", "X-Client-IP-Signature": "invalid"},
        json={**lead_payload(), "email": "forged-visitor@example.com"},
    )
    assert forged_visitor.status_code == 429

    client_ip = "203.0.113.10"
    secret = "change-me-in-production"
    signature = hmac.new(secret.encode(), client_ip.encode(), hashlib.sha256).hexdigest()
    other_visitor = await lead_client.post(
        "/api/v1/public/leads",
        headers={"X-Client-IP": client_ip, "X-Client-IP-Signature": signature},
        json={**lead_payload(), "email": "other-visitor@example.com"},
    )
    assert other_visitor.status_code == 201


@pytest.mark.asyncio
async def test_public_routes_validate_request_data(lead_client: AsyncClient):
    missing_key = await lead_client.post("/api/v1/public/leads/views")
    assert missing_key.status_code == 422

    invalid_lead = await lead_client.post(
        "/api/v1/public/leads?o=instagram",
        json={"full_name": "A", "email": "invalid", "company_name": "", "privacy_consent": False},
    )
    assert invalid_lead.status_code == 422

    extra_field = await lead_client.post(
        "/api/v1/public/leads",
        json={
            "full_name": "Valid Name",
            "email": "valid@example.com",
            "company_name": "Valid Company",
            "privacy_consent": True,
            "owner_id": str(uuid.uuid4()),
        },
    )
    assert extra_field.status_code == 422

    invalid_id = await lead_client.get("/api/v1/leads/not-an-uuid")
    assert invalid_id.status_code == 401


@pytest.mark.asyncio
async def test_public_lead_accepts_only_required_fields(lead_client: AsyncClient):
    response = await lead_client.post(
        "/api/v1/public/leads?o=direct",
        json={
            "full_name": "Katherine Johnson",
            "email": "katherine@example.com",
            "company_name": "Orbital Systems",
            "privacy_consent": True,
        },
    )
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_public_student_lead_submission(lead_client: AsyncClient):
    response = await lead_client.post(
        "/api/v1/public/leads/students?o=campus",
        json={
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "semester": "6th semester",
            "linkedin_url": "https://linkedin.com/in/mary-jackson",
            "github_url": "https://github.com/mary-jackson",
            "area_of_interest": "Aerospace",
            "message": "I want to learn more",
            "privacy_consent": True,
        },
    )

    assert response.status_code == 201
    async with lead_client.lead_session_factory() as session:
        lead = await session.get(Lead, uuid.UUID(response.json()["id"]))
    assert lead.lead_type == LeadType.STUDENT
    assert lead.company_name is None
    assert lead.institution_name == "Hampton Institute"
    assert lead.course_name == "Engineering"
    assert lead.source == "campus"
    assert lead.institution_id is not None
    assert lead.course_id is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "course_name": "Engineering",
            "privacy_consent": True,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "privacy_consent": False,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "linkedin_url": "not-a-url",
            "privacy_consent": True,
        },
        {
            "full_name": "Mary Jackson",
            "email": "mary@example.com",
            "institution_name": "Hampton Institute",
            "course_name": "Engineering",
            "company_name": "Unexpected Company",
            "privacy_consent": True,
        },
    ],
)
async def test_public_student_lead_validates_request(lead_client: AsyncClient, payload: dict):
    response = await lead_client.post("/api/v1/public/leads/students", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_public_catalogs_only_return_available_items(lead_client: AsyncClient):
    async with lead_client.lead_session_factory() as session:
        approved = EducationalInstitution(
            name="Faculdade de Tecnologia de Jacareí",
            normalized_name="faculdade de tecnologia de jacarei",
            status=CatalogStatus.APPROVED,
        )
        session.add_all(
            [
                approved,
                EducationalInstitution(
                    name="Fatec Pendente",
                    normalized_name="fatec pendente",
                    status=CatalogStatus.PENDING,
                ),
                AcademicCourse(
                    name="Análise e Desenvolvimento de Sistemas",
                    normalized_name="analise e desenvolvimento de sistemas",
                    status=CatalogStatus.APPROVED,
                ),
                InterestArea(code="backend", name="Backend"),
                InterestArea(code="inactive", name="Inativa", active=False),
            ]
        )
        await session.flush()
        session.add(
            EducationalInstitutionAlias(
                institution_id=approved.id,
                name="Fatec Jacareí",
                normalized_name="fatec jacarei",
            )
        )
        await session.commit()

    institutions = await lead_client.get("/api/v1/public/leads/catalog/institutions?q=FATEC")
    courses = await lead_client.get("/api/v1/public/leads/catalog/courses?q=desenvolvimento")
    areas = await lead_client.get("/api/v1/public/leads/catalog/interest-areas")

    assert institutions.status_code == 200
    assert [item["name"] for item in institutions.json()] == ["Faculdade de Tecnologia de Jacareí"]
    assert [item["name"] for item in courses.json()] == ["Análise e Desenvolvimento de Sistemas"]
    assert [item["code"] for item in areas.json()] == ["backend"]
    assert (
        await lead_client.get("/api/v1/public/leads/catalog/institutions?q=x")
    ).status_code == 422
    assert (await lead_client.get("/api/v1/public/leads/catalog/institutions?q=!!")).json() == []


@pytest.mark.asyncio
async def test_public_student_lead_accepts_normalized_catalog_ids(lead_client: AsyncClient):
    async with lead_client.lead_session_factory() as session:
        institution = EducationalInstitution(
            name="Universidade de São Paulo",
            normalized_name="universidade de sao paulo",
            status=CatalogStatus.APPROVED,
        )
        course = AcademicCourse(
            name="Sistemas de Informação",
            normalized_name="sistemas de informacao",
            status=CatalogStatus.APPROVED,
        )
        backend = InterestArea(code="backend", name="Backend")
        product = InterestArea(code="product", name="Produto")
        session.add_all([institution, course, backend, product])
        await session.commit()

    response = await lead_client.post(
        "/api/v1/public/leads/students?o=campus",
        json={
            "full_name": "Radia Perlman",
            "email": "radia@example.com",
            "institution_id": str(institution.id),
            "course_id": str(course.id),
            "semester_number": 7,
            "interest_area_ids": [str(product.id), str(backend.id)],
            "privacy_consent": True,
        },
    )

    assert response.status_code == 201
    async with lead_client.lead_session_factory() as session:
        lead = await session.get(Lead, uuid.UUID(response.json()["id"]))
        links = list(
            await session.scalars(
                select(LeadInterestArea).where(LeadInterestArea.lead_id == lead.id)
            )
        )
    assert lead.institution_name == "Universidade de São Paulo"
    assert lead.course_name == "Sistemas de Informação"
    assert lead.semester == "7º semestre"
    assert lead.semester_number == 7
    assert lead.area_of_interest == "Produto"
    assert {link.interest_area_id for link in links} == {product.id, backend.id}


@pytest.mark.asyncio
async def test_public_student_lead_creates_hidden_pending_catalogs(lead_client: AsyncClient):
    response = await lead_client.post(
        "/api/v1/public/leads/students",
        json={
            "full_name": "Evelyn Boyd Granville",
            "email": "evelyn@example.com",
            "institution_name": "  Nova   Universidade ",
            "course_name": "Computação Aplicada",
            "semester_number": 2,
            "interest_area_ids": [],
            "privacy_consent": True,
        },
    )

    assert response.status_code == 201
    duplicate = await lead_client.post(
        "/api/v1/public/leads/students",
        json={
            "full_name": "Karen Spärck Jones",
            "email": "karen@example.com",
            "institution_name": "NOVA UNIVERSIDADE",
            "course_name": "Computação Aplicada",
            "privacy_consent": True,
        },
    )
    assert duplicate.status_code == 201
    async with lead_client.lead_session_factory() as session:
        institution = await session.scalar(
            select(EducationalInstitution).where(
                EducationalInstitution.normalized_name == "nova universidade"
            )
        )
        course = await session.scalar(
            select(AcademicCourse).where(AcademicCourse.normalized_name == "computacao aplicada")
        )
        institution_count = len(list(await session.scalars(select(EducationalInstitution))))
        course_count = len(list(await session.scalars(select(AcademicCourse))))
    assert institution is not None and institution.status == CatalogStatus.PENDING
    assert course is not None and course.status == CatalogStatus.PENDING
    assert institution_count == 1
    assert course_count == 1

    hidden = await lead_client.get("/api/v1/public/leads/catalog/institutions?q=nova universidade")
    assert hidden.json() == []


@pytest.mark.asyncio
async def test_normalized_student_payload_rejects_ambiguous_or_invalid_catalogs(
    lead_client: AsyncClient,
):
    pending = EducationalInstitution(
        name="Instituição Pendente",
        normalized_name="instituicao pendente",
        status=CatalogStatus.PENDING,
    )
    async with lead_client.lead_session_factory() as session:
        session.add(pending)
        await session.commit()

    base = {
        "full_name": "Barbara Liskov",
        "email": "barbara@example.com",
        "institution_name": "MIT",
        "course_name": "Computer Science",
        "privacy_consent": True,
    }
    ambiguous = await lead_client.post(
        "/api/v1/public/leads/students",
        json={**base, "institution_id": str(pending.id)},
    )
    unavailable = await lead_client.post(
        "/api/v1/public/leads/students",
        json={
            **base,
            "institution_id": str(pending.id),
            "institution_name": None,
        },
    )
    duplicate_areas = await lead_client.post(
        "/api/v1/public/leads/students",
        json={**base, "interest_area_ids": [str(uuid.uuid4())] * 2},
    )
    invalid_semester = await lead_client.post(
        "/api/v1/public/leads/students",
        json={**base, "semester_number": True},
    )
    unknown_area = await lead_client.post(
        "/api/v1/public/leads/students",
        json={**base, "interest_area_ids": [str(uuid.uuid4())]},
    )

    assert ambiguous.status_code == 422
    assert unavailable.status_code == 422
    assert duplicate_areas.status_code == 422
    assert invalid_semester.status_code == 422
    assert unknown_area.status_code == 422


@pytest.mark.asyncio
async def test_authenticated_lead_management(lead_client: AsyncClient):
    await lead_client.post(
        "/api/v1/auth/register",
        json={
            "email": "admin@example.com",
            "password": "SenhaSegura12345",
            "nome": "Admin",
        },
    )
    async with lead_client.lead_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == "admin@example.com"))
        user.is_superuser = True
        await session.commit()
    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "admin@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = await lead_client.post("/api/v1/public/leads?o=eventox", json=lead_payload())
    lead_id = created.json()["id"]

    listed = await lead_client.get("/api/v1/leads", headers=headers)
    assert listed.status_code == 200
    assert listed.json()[0]["source"] == "eventox"
    assert listed.json()[0]["lead_type"] == "company"

    student = await lead_client.post(
        "/api/v1/public/leads/students?o=campus",
        json={
            "full_name": "Annie Easley",
            "email": "annie@example.com",
            "institution_name": "Cleveland State University",
            "course_name": "Mathematics",
            "privacy_consent": True,
        },
    )
    student_admin = await lead_client.get(f"/api/v1/leads/{student.json()['id']}", headers=headers)
    assert student_admin.status_code == 200
    assert student_admin.json()["lead_type"] == "student"
    assert student_admin.json()["company_name"] is None
    assert student_admin.json()["institution_name"] == "Cleveland State University"

    updated = await lead_client.patch(
        f"/api/v1/leads/{lead_id}/status",
        headers=headers,
        json={"status": "contacted"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "contacted"

    fetched = await lead_client.get(f"/api/v1/leads/{lead_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["id"] == lead_id

    missing = await lead_client.get(f"/api/v1/leads/{uuid.uuid4()}", headers=headers)
    assert missing.status_code == 404

    deleted = await lead_client.delete(f"/api/v1/leads/{lead_id}", headers=headers)
    assert deleted.status_code == 204
    deleted_lead = await lead_client.get(f"/api/v1/leads/{lead_id}", headers=headers)
    assert deleted_lead.status_code == 404


@pytest.mark.asyncio
async def test_regular_user_cannot_manage_leads(lead_client: AsyncClient):
    await lead_client.post(
        "/api/v1/auth/register",
        json={
            "email": "regular@example.com",
            "password": "SenhaSegura12345",
            "nome": "Regular",
        },
    )
    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "regular@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    response = await lead_client.get("/api/v1/leads", headers=headers)
    assert response.status_code == 403
    catalogs = await lead_client.get("/api/v1/leads/catalog/institutions", headers=headers)
    assert catalogs.status_code == 403


@pytest.mark.asyncio
async def test_superuser_approves_and_merges_catalogs(lead_client: AsyncClient):
    await lead_client.post(
        "/api/v1/auth/register",
        json={
            "email": "catalog-admin@example.com",
            "password": "SenhaSegura12345",
            "nome": "Catalog Admin",
        },
    )
    async with lead_client.lead_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == "catalog-admin@example.com"))
        user.is_superuser = True

        institution_target = EducationalInstitution(
            name="Universidade Canônica",
            normalized_name="universidade canonica",
            status=CatalogStatus.APPROVED,
        )
        institution_source = EducationalInstitution(
            name="Universidade Antiga",
            normalized_name="universidade antiga",
            status=CatalogStatus.PENDING,
        )
        institution_to_approve = EducationalInstitution(
            name="Universidade para Aprovar",
            normalized_name="universidade para aprovar",
            status=CatalogStatus.PENDING,
        )
        course_target = AcademicCourse(
            name="Curso Canônico",
            normalized_name="curso canonico",
            status=CatalogStatus.APPROVED,
        )
        course_source = AcademicCourse(
            name="Curso Antigo",
            normalized_name="curso antigo",
            status=CatalogStatus.PENDING,
        )
        course_to_approve = AcademicCourse(
            name="Curso para Aprovar",
            normalized_name="curso para aprovar",
            status=CatalogStatus.PENDING,
        )
        session.add_all(
            [
                institution_target,
                institution_source,
                institution_to_approve,
                course_target,
                course_source,
                course_to_approve,
            ]
        )
        await session.flush()
        session.add_all(
            [
                EducationalInstitutionAlias(
                    institution_id=institution_source.id,
                    name="UA",
                    normalized_name="ua",
                ),
                AcademicCourseAlias(
                    course_id=course_source.id,
                    name="CA",
                    normalized_name="ca",
                ),
                Lead(
                    lead_type=LeadType.STUDENT,
                    full_name="Frances Allen",
                    email="frances@example.com",
                    institution_id=institution_source.id,
                    institution_name=institution_source.name,
                    course_id=course_source.id,
                    course_name=course_source.name,
                    privacy_consent=True,
                ),
            ]
        )
        await session.commit()

    login = await lead_client.post(
        "/api/v1/auth/jwt/login",
        data={"username": "catalog-admin@example.com", "password": "SenhaSegura12345"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    pending = await lead_client.get("/api/v1/leads/catalog/institutions", headers=headers)
    pending_courses = await lead_client.get("/api/v1/leads/catalog/courses", headers=headers)
    assert pending.status_code == 200
    assert {item["name"] for item in pending.json()} == {
        "Universidade Antiga",
        "Universidade para Aprovar",
    }
    assert {item["name"] for item in pending_courses.json()} == {
        "Curso Antigo",
        "Curso para Aprovar",
    }

    approved = await lead_client.patch(
        f"/api/v1/leads/catalog/institutions/{institution_to_approve.id}/approve",
        headers=headers,
    )
    approved_course = await lead_client.patch(
        f"/api/v1/leads/catalog/courses/{course_to_approve.id}/approve",
        headers=headers,
    )
    institution_merge = await lead_client.post(
        f"/api/v1/leads/catalog/institutions/{institution_source.id}/merge",
        headers=headers,
        json={"target_id": str(institution_target.id)},
    )
    course_merge = await lead_client.post(
        f"/api/v1/leads/catalog/courses/{course_source.id}/merge",
        headers=headers,
        json={"target_id": str(course_target.id)},
    )

    assert approved.status_code == 200
    assert approved_course.status_code == 200
    assert approved.json()["status"] == "approved"
    assert approved.json()["reviewed_by_id"] == str(user.id)
    assert institution_merge.status_code == 200
    assert institution_merge.json()["status"] == "merged"
    assert institution_merge.json()["merged_into_id"] == str(institution_target.id)
    assert course_merge.status_code == 200

    async with lead_client.lead_session_factory() as session:
        lead = await session.scalar(select(Lead).where(Lead.email == "frances@example.com"))
        target = await session.scalar(
            select(EducationalInstitution)
            .where(EducationalInstitution.id == institution_target.id)
            .options(selectinload(EducationalInstitution.aliases))
        )
        merged_course = await session.scalar(
            select(AcademicCourse)
            .where(AcademicCourse.id == course_target.id)
            .options(selectinload(AcademicCourse.aliases))
        )
    assert lead.institution_id == institution_target.id
    assert lead.institution_name == institution_target.name
    assert lead.course_id == course_target.id
    assert lead.course_name == course_target.name
    assert {alias.normalized_name for alias in target.aliases} == {"ua", "universidade antiga"}
    assert {alias.normalized_name for alias in merged_course.aliases} == {"ca", "curso antigo"}

    normalized_from_merged_name = await lead_client.post(
        "/api/v1/public/leads/students",
        json={
            "full_name": "Jean Sammet",
            "email": "jean@example.com",
            "institution_name": institution_source.name,
            "course_name": course_source.name,
            "privacy_consent": True,
        },
    )
    assert normalized_from_merged_name.status_code == 201
    async with lead_client.lead_session_factory() as session:
        normalized_lead = await session.scalar(select(Lead).where(Lead.email == "jean@example.com"))
    assert normalized_lead.institution_id == institution_target.id
    assert normalized_lead.course_id == course_target.id

    self_merge = await lead_client.post(
        f"/api/v1/leads/catalog/institutions/{institution_target.id}/merge",
        headers=headers,
        json={"target_id": str(institution_target.id)},
    )
    assert self_merge.status_code == 409
    already_approved = await lead_client.patch(
        f"/api/v1/leads/catalog/institutions/{institution_target.id}/approve",
        headers=headers,
    )
    missing_merge = await lead_client.post(
        f"/api/v1/leads/catalog/institutions/{uuid.uuid4()}/merge",
        headers=headers,
        json={"target_id": str(institution_target.id)},
    )
    merged_again = await lead_client.post(
        f"/api/v1/leads/catalog/institutions/{institution_source.id}/merge",
        headers=headers,
        json={"target_id": str(institution_target.id)},
    )
    invalid_target = await lead_client.post(
        f"/api/v1/leads/catalog/institutions/{institution_target.id}/merge",
        headers=headers,
        json={"target_id": str(institution_source.id)},
    )
    assert already_approved.status_code == 409
    assert missing_merge.status_code == 404
    assert merged_again.status_code == 409
    assert invalid_target.status_code == 409
