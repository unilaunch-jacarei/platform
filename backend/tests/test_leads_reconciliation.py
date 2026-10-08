import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.database import Base
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
from backend.domains.leads.reconciliation import (
    parse_legacy_semester,
    reconcile_student_leads,
)


@pytest_asyncio.fixture
async def reconciliation_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


def test_parse_legacy_semester_is_conservative() -> None:
    assert parse_legacy_semester("4º semestre") == 4
    assert parse_legacy_semester("período 2 de 8") is None
    assert parse_legacy_semester("13") is None
    assert parse_legacy_semester(None) is None


@pytest.mark.asyncio
async def test_reconciliation_normalizes_known_and_unknown_values(
    reconciliation_session: AsyncSession,
) -> None:
    institution = EducationalInstitution(
        name="Faculdade de Tecnologia de Jacareí",
        normalized_name="faculdade de tecnologia de jacarei",
        status=CatalogStatus.APPROVED,
    )
    course = AcademicCourse(
        name="Análise e Desenvolvimento de Sistemas",
        normalized_name="analise e desenvolvimento de sistemas",
        status=CatalogStatus.APPROVED,
    )
    backend = InterestArea(code="backend", name="Backend")
    reconciliation_session.add_all([institution, course, backend])
    await reconciliation_session.flush()
    reconciliation_session.add_all(
        [
            EducationalInstitutionAlias(
                institution_id=institution.id,
                name="Fatec Jacareí",
                normalized_name="fatec jacarei",
            ),
            AcademicCourseAlias(
                course_id=course.id,
                name="ADS",
                normalized_name="ads",
            ),
            Lead(
                lead_type=LeadType.STUDENT,
                full_name="Ada Lovelace",
                email="ada@example.com",
                institution_name="  FATEC Jacareí ",
                course_name="ads",
                semester="4º semestre",
                area_of_interest="Backend",
                privacy_consent=True,
            ),
            Lead(
                lead_type=LeadType.STUDENT,
                full_name="Grace Hopper",
                email="grace@example.com",
                institution_name="Instituto Novo",
                course_name="Curso Novo",
                semester="período indefinido",
                area_of_interest="Aeroespacial",
                privacy_consent=True,
            ),
        ]
    )
    await reconciliation_session.commit()

    assert await reconcile_student_leads(reconciliation_session) == 2
    assert await reconcile_student_leads(reconciliation_session) == 0

    leads = list(await reconciliation_session.scalars(select(Lead).order_by(Lead.email)))
    known, unknown = leads
    assert known.institution_id == institution.id
    assert known.course_id == course.id
    assert known.semester_number == 4
    assert unknown.semester_number is None

    pending_institution = await reconciliation_session.scalar(
        select(EducationalInstitution).where(
            EducationalInstitution.normalized_name == "instituto novo"
        )
    )
    pending_course = await reconciliation_session.scalar(
        select(AcademicCourse).where(AcademicCourse.normalized_name == "curso novo")
    )
    assert pending_institution is not None
    assert pending_institution.status == CatalogStatus.PENDING
    assert pending_course is not None
    assert pending_course.status == CatalogStatus.PENDING
    assert unknown.institution_id == pending_institution.id
    assert unknown.course_id == pending_course.id
    assert (
        await reconciliation_session.scalar(select(func.count()).select_from(LeadInterestArea)) == 1
    )
