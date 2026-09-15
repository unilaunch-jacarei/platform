import asyncio
import re
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.database import close_db, get_session_factory
from backend.domains.leads.catalog import normalize_catalog_name
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

LEGACY_INTEREST_CODES = {
    "backend": "backend",
    "frontend": "frontend",
    "devops": "devops-cloud",
    "produto": "product",
    "ux ui": "ux-ui",
}


def parse_legacy_semester(value: str | None) -> int | None:
    numbers = re.findall(r"\d+", value or "")
    if len(numbers) != 1:
        return None
    semester = int(numbers[0])
    return semester if 1 <= semester <= 12 else None


async def _named_lookup[NamedCatalog: (EducationalInstitution, AcademicCourse)](
    session: AsyncSession,
    model: type[NamedCatalog],
    alias_model: type[EducationalInstitutionAlias] | type[AcademicCourseAlias],
) -> dict[str, NamedCatalog]:
    items = list(await session.scalars(select(model)))
    by_id = {item.id: item for item in items}
    lookup = {item.normalized_name: item for item in items}
    aliases = list(await session.scalars(select(alias_model)))
    foreign_key = "institution_id" if model is EducationalInstitution else "course_id"
    for alias in aliases:
        item = by_id[getattr(alias, foreign_key)]
        lookup[alias.normalized_name] = item
    return lookup


async def _resolve_or_create[NamedCatalog: (EducationalInstitution, AcademicCourse)](
    session: AsyncSession,
    model: type[NamedCatalog],
    lookup: dict[str, NamedCatalog],
    value: str | None,
) -> NamedCatalog | None:
    if value is None:
        return None
    name = " ".join(value.split())
    normalized_name = normalize_catalog_name(name)
    if not normalized_name:
        return None
    if existing := lookup.get(normalized_name):
        return existing

    item = model(name=name, normalized_name=normalized_name, status=CatalogStatus.PENDING)
    try:
        async with session.begin_nested():
            session.add(item)
            await session.flush()
    except IntegrityError:
        item = await session.scalar(select(model).where(model.normalized_name == normalized_name))
        if item is None:
            raise RuntimeError("Catalog conflict could not be resolved") from None
    lookup[normalized_name] = item
    return item


def _interest_area_lookup(areas: Sequence[InterestArea]) -> dict[str, InterestArea]:
    by_code = {area.code: area for area in areas if area.active}
    lookup = {normalize_catalog_name(area.name): area for area in areas if area.active}
    for legacy_name, code in LEGACY_INTEREST_CODES.items():
        if area := by_code.get(code):
            lookup[legacy_name] = area
    return lookup


async def reconcile_student_leads(session: AsyncSession) -> int:
    institution_lookup = await _named_lookup(
        session, EducationalInstitution, EducationalInstitutionAlias
    )
    course_lookup = await _named_lookup(session, AcademicCourse, AcademicCourseAlias)
    areas = list(await session.scalars(select(InterestArea)))
    area_lookup = _interest_area_lookup(areas)
    leads = list(
        await session.scalars(
            select(Lead)
            .where(Lead.lead_type == LeadType.STUDENT)
            .options(selectinload(Lead.interest_area_links))
        )
    )

    changed = 0
    for lead in leads:
        lead_changed = False
        if lead.institution_id is None:
            institution = await _resolve_or_create(
                session, EducationalInstitution, institution_lookup, lead.institution_name
            )
            if institution is not None:
                lead.institution_id = institution.id
                lead_changed = True

        if lead.course_id is None:
            course = await _resolve_or_create(
                session, AcademicCourse, course_lookup, lead.course_name
            )
            if course is not None:
                lead.course_id = course.id
                lead_changed = True

        if lead.semester_number is None:
            semester_number = parse_legacy_semester(lead.semester)
            if semester_number is not None:
                lead.semester_number = semester_number
                lead_changed = True

        if not lead.interest_area_links and lead.area_of_interest:
            area = area_lookup.get(normalize_catalog_name(lead.area_of_interest))
            if area is not None:
                session.add(LeadInterestArea(lead_id=lead.id, interest_area_id=area.id))
                lead_changed = True

        changed += int(lead_changed)

    await session.commit()
    return changed


async def _run() -> None:
    try:
        async with get_session_factory()() as session:
            changed = await reconcile_student_leads(session)
            print(f"Reconciled {changed} student leads")
    finally:
        await close_db()


def run() -> None:
    asyncio.run(_run())
