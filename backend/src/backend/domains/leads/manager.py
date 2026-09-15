from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.domains.leads.catalog import LEGACY_INTEREST_AREA_CODES, normalize_catalog_name
from backend.domains.leads.models import (
    AcademicCourse,
    AcademicCourseAlias,
    CatalogStatus,
    EducationalInstitution,
    EducationalInstitutionAlias,
    InterestArea,
    Lead,
    LeadInterestArea,
    LeadPageView,
)
from backend.domains.leads.schemas import (
    LeadCreate,
    LeadStatusUpdate,
    LeadViewCreate,
    StudentLeadCreate,
)
from backend.error import ConflictError, NotFoundError, UnprocessableEntityError

NamedCatalog = EducationalInstitution | AcademicCourse
NamedCatalogModel = type[EducationalInstitution] | type[AcademicCourse]
NamedAliasModel = type[EducationalInstitutionAlias] | type[AcademicCourseAlias]


class LeadService:
    """Application operations for public lead capture and administration."""

    async def create(self, session: AsyncSession, data: LeadCreate | StudentLeadCreate) -> Lead:
        if isinstance(data, StudentLeadCreate):
            return await self.create_student(session, data)
        lead = Lead(**data.model_dump(mode="json"))
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
        return lead

    async def create_student(self, session: AsyncSession, data: StudentLeadCreate) -> Lead:
        values = data.model_dump(
            mode="json", exclude={"interest_area_ids", "institution_id", "course_id"}
        )
        interest_area_ids = data.interest_area_ids
        institution_id = data.institution_id
        course_id = data.course_id

        institution = await self._resolve_institution(
            session, institution_id, values["institution_name"]
        )
        course = await self._resolve_course(session, course_id, values["course_name"])
        areas = await self._resolve_interest_areas(
            session, interest_area_ids, values["area_of_interest"]
        )

        values["institution_id"] = institution.id
        values["institution_name"] = institution.name
        values["course_id"] = course.id
        values["course_name"] = course.name
        if values["semester_number"] is not None:
            values["semester"] = f"{values['semester_number']}º semestre"
        if interest_area_ids is not None:
            values["area_of_interest"] = areas[0].name if areas else None

        lead = Lead(**values)
        session.add(lead)
        await session.flush()
        session.add_all(
            [LeadInterestArea(lead_id=lead.id, interest_area_id=area.id) for area in areas]
        )
        await session.commit()
        await session.refresh(lead)
        return lead

    async def record_page_view(
        self, session: AsyncSession, data: LeadViewCreate
    ) -> tuple[LeadPageView, bool]:
        existing = await self._find_page_view(session, data.event_key)
        if existing is not None:
            return existing, False

        page_view = LeadPageView(**data.model_dump())
        created = True
        try:
            async with session.begin_nested():
                session.add(page_view)
                await session.flush()
        except IntegrityError:
            created = False

        if not created:
            page_view = await self._find_page_view(session, data.event_key)
            if page_view is None:
                raise RuntimeError("Page view conflict could not be resolved")

        await session.commit()
        return page_view, created

    async def list(self, session: AsyncSession, limit: int = 100, offset: int = 0) -> list[Lead]:
        result = await session.scalars(
            self._lead_query().order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result)

    async def get(self, session: AsyncSession, lead_id: uuid.UUID) -> Lead:
        lead = await session.scalar(self._lead_query().where(Lead.id == lead_id))
        if lead is None:
            raise NotFoundError("Lead não encontrado")
        return lead

    async def update_status(
        self, session: AsyncSession, lead_id: uuid.UUID, data: LeadStatusUpdate
    ) -> Lead:
        lead = await self.get(session, lead_id)
        lead.status = data.status
        await session.commit()
        await session.refresh(lead)
        return lead

    async def delete(self, session: AsyncSession, lead_id: uuid.UUID) -> None:
        lead = await self.get(session, lead_id)
        await session.delete(lead)
        await session.commit()

    async def purge_before(self, session: AsyncSession, cutoff: datetime) -> int:
        expired_leads = select(Lead.id).where(Lead.created_at < cutoff)
        await session.execute(
            delete(LeadInterestArea).where(LeadInterestArea.lead_id.in_(expired_leads))
        )
        result = await session.execute(delete(Lead).where(Lead.created_at < cutoff))
        await session.commit()
        return result.rowcount or 0

    async def _find_page_view(self, session: AsyncSession, event_key: str) -> LeadPageView | None:
        return await session.scalar(select(LeadPageView).where(LeadPageView.event_key == event_key))

    async def search_institutions(
        self, session: AsyncSession, query: str, limit: int
    ) -> list[EducationalInstitution]:
        normalized = normalize_catalog_name(query)
        if not normalized:
            return []
        result = await session.scalars(
            select(EducationalInstitution)
            .outerjoin(EducationalInstitutionAlias)
            .where(
                EducationalInstitution.status == CatalogStatus.APPROVED,
                or_(
                    EducationalInstitution.normalized_name.contains(normalized),
                    EducationalInstitutionAlias.normalized_name.contains(normalized),
                ),
            )
            .distinct()
            .order_by(EducationalInstitution.name, EducationalInstitution.id)
            .limit(limit)
        )
        return list(result)

    async def search_courses(
        self, session: AsyncSession, query: str, limit: int
    ) -> list[AcademicCourse]:
        normalized = normalize_catalog_name(query)
        if not normalized:
            return []
        result = await session.scalars(
            select(AcademicCourse)
            .outerjoin(AcademicCourseAlias)
            .where(
                AcademicCourse.status == CatalogStatus.APPROVED,
                or_(
                    AcademicCourse.normalized_name.contains(normalized),
                    AcademicCourseAlias.normalized_name.contains(normalized),
                ),
            )
            .distinct()
            .order_by(AcademicCourse.name, AcademicCourse.id)
            .limit(limit)
        )
        return list(result)

    async def list_interest_areas(self, session: AsyncSession) -> list[InterestArea]:
        result = await session.scalars(
            select(InterestArea)
            .where(InterestArea.active.is_(True))
            .order_by(InterestArea.name, InterestArea.id)
        )
        return list(result)

    async def list_institutions(
        self,
        session: AsyncSession,
        catalog_status: CatalogStatus | None,
        limit: int,
        offset: int,
    ) -> list[EducationalInstitution]:
        query = select(EducationalInstitution).options(selectinload(EducationalInstitution.aliases))
        if catalog_status is not None:
            query = query.where(EducationalInstitution.status == catalog_status)
        result = await session.scalars(
            query.order_by(EducationalInstitution.created_at, EducationalInstitution.id)
            .offset(offset)
            .limit(limit)
        )
        return list(result)

    async def list_courses(
        self,
        session: AsyncSession,
        catalog_status: CatalogStatus | None,
        limit: int,
        offset: int,
    ) -> list[AcademicCourse]:
        query = select(AcademicCourse).options(selectinload(AcademicCourse.aliases))
        if catalog_status is not None:
            query = query.where(AcademicCourse.status == catalog_status)
        result = await session.scalars(
            query.order_by(AcademicCourse.created_at, AcademicCourse.id).offset(offset).limit(limit)
        )
        return list(result)

    async def approve_institution(
        self, session: AsyncSession, item_id: uuid.UUID, reviewer_id: uuid.UUID
    ) -> EducationalInstitution:
        return await self._approve_catalog(
            session, EducationalInstitution, item_id, reviewer_id, "Instituição"
        )

    async def approve_course(
        self, session: AsyncSession, item_id: uuid.UUID, reviewer_id: uuid.UUID
    ) -> AcademicCourse:
        return await self._approve_catalog(session, AcademicCourse, item_id, reviewer_id, "Curso")

    async def merge_institution(
        self,
        session: AsyncSession,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        reviewer_id: uuid.UUID,
    ) -> EducationalInstitution:
        return await self._merge_catalog(
            session,
            EducationalInstitution,
            EducationalInstitutionAlias,
            "institution_id",
            Lead.institution_id,
            "institution_name",
            source_id,
            target_id,
            reviewer_id,
            "Instituição",
        )

    async def merge_course(
        self,
        session: AsyncSession,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        reviewer_id: uuid.UUID,
    ) -> AcademicCourse:
        return await self._merge_catalog(
            session,
            AcademicCourse,
            AcademicCourseAlias,
            "course_id",
            Lead.course_id,
            "course_name",
            source_id,
            target_id,
            reviewer_id,
            "Curso",
        )

    def _lead_query(self):
        return select(Lead).options(
            selectinload(Lead.institution),
            selectinload(Lead.course),
            selectinload(Lead.interest_areas),
            selectinload(Lead.interest_area_links),
        )

    async def _resolve_institution(
        self, session: AsyncSession, item_id: uuid.UUID | None, name: str | None
    ) -> EducationalInstitution:
        return await self._resolve_named_catalog(
            session,
            EducationalInstitution,
            EducationalInstitutionAlias,
            "institution_id",
            item_id,
            name,
            "Instituição",
        )

    async def _resolve_course(
        self, session: AsyncSession, item_id: uuid.UUID | None, name: str | None
    ) -> AcademicCourse:
        return await self._resolve_named_catalog(
            session,
            AcademicCourse,
            AcademicCourseAlias,
            "course_id",
            item_id,
            name,
            "Curso",
        )

    async def _resolve_named_catalog(
        self,
        session: AsyncSession,
        model: NamedCatalogModel,
        alias_model: NamedAliasModel,
        alias_foreign_key: str,
        item_id: uuid.UUID | None,
        name: str | None,
        label: str,
    ) -> NamedCatalog:
        if item_id is not None:
            item = await session.get(model, item_id)
            if item is None or item.status != CatalogStatus.APPROVED:
                raise UnprocessableEntityError(f"{label} inválido ou indisponível")
            return item

        normalized_name = normalize_catalog_name(name or "")
        if not normalized_name:
            raise UnprocessableEntityError(f"{label} inválido")
        item = await session.scalar(select(model).where(model.normalized_name == normalized_name))
        if item is None:
            item = await session.scalar(
                select(model)
                .join(alias_model, getattr(alias_model, alias_foreign_key) == model.id)
                .where(alias_model.normalized_name == normalized_name)
            )
        if item is not None:
            if item.status == CatalogStatus.MERGED and item.merged_into_id is not None:
                merged_item = await session.get(model, item.merged_into_id)
                if merged_item is not None:
                    return merged_item
            return item

        item = model(
            name=name,
            normalized_name=normalized_name,
            status=CatalogStatus.PENDING,
        )
        try:
            async with session.begin_nested():
                session.add(item)
                await session.flush()
        except IntegrityError:
            item = await session.scalar(
                select(model).where(model.normalized_name == normalized_name)
            )
            if item is None:
                raise RuntimeError("Catalog conflict could not be resolved") from None
        return item

    async def _resolve_interest_areas(
        self,
        session: AsyncSession,
        item_ids: list[uuid.UUID] | None,
        legacy_name: str | None,
    ) -> list[InterestArea]:
        if item_ids is not None:
            if not item_ids:
                return []
            areas = list(
                await session.scalars(
                    select(InterestArea).where(
                        InterestArea.id.in_(item_ids), InterestArea.active.is_(True)
                    )
                )
            )
            if len(areas) != len(item_ids):
                raise UnprocessableEntityError("Uma ou mais áreas de interesse são inválidas")
            by_id = {area.id: area for area in areas}
            return [by_id[item_id] for item_id in item_ids]

        if legacy_name is None:
            return []
        normalized_name = normalize_catalog_name(legacy_name)
        if code := LEGACY_INTEREST_AREA_CODES.get(normalized_name):
            area = await session.scalar(
                select(InterestArea).where(InterestArea.code == code, InterestArea.active.is_(True))
            )
            return [area] if area is not None else []
        areas = await self.list_interest_areas(session)
        return [area for area in areas if normalize_catalog_name(area.name) == normalized_name][:1]

    async def _approve_catalog(
        self,
        session: AsyncSession,
        model: NamedCatalogModel,
        item_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        label: str,
    ) -> NamedCatalog:
        item = await session.scalar(
            select(model).where(model.id == item_id).options(selectinload(model.aliases))
        )
        if item is None:
            raise NotFoundError(f"{label} não encontrado")
        if item.status != CatalogStatus.PENDING:
            raise ConflictError(f"{label} não está pendente")
        item.status = CatalogStatus.APPROVED
        item.reviewed_by_id = reviewer_id
        item.reviewed_at = datetime.now(UTC)
        await session.commit()
        approved = await session.scalar(
            select(model).where(model.id == item.id).options(selectinload(model.aliases))
        )
        if approved is None:
            raise RuntimeError("Approved catalog could not be reloaded")
        return approved

    async def _merge_catalog(
        self,
        session: AsyncSession,
        model: NamedCatalogModel,
        alias_model: NamedAliasModel,
        alias_foreign_key: str,
        lead_foreign_key,
        legacy_name_field: str,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        reviewer_id: uuid.UUID,
        label: str,
    ) -> NamedCatalog:
        if source_id == target_id:
            raise ConflictError(f"{label} não pode ser mesclado nele mesmo")
        items = list(
            await session.scalars(
                select(model)
                .where(model.id.in_([source_id, target_id]))
                .options(selectinload(model.aliases))
            )
        )
        by_id = {item.id: item for item in items}
        source = by_id.get(source_id)
        target = by_id.get(target_id)
        if source is None or target is None:
            raise NotFoundError(f"{label} de origem ou destino não encontrado")
        if source.status == CatalogStatus.MERGED:
            raise ConflictError(f"{label} de origem já foi mesclado")
        if target.status != CatalogStatus.APPROVED:
            raise ConflictError(f"{label} de destino deve estar aprovado")

        await session.execute(
            update(Lead)
            .where(lead_foreign_key == source.id)
            .values({lead_foreign_key.key: target.id, legacy_name_field: target.name})
        )
        await self._transfer_aliases(
            session, model, alias_model, alias_foreign_key, source, target, label
        )
        source.status = CatalogStatus.MERGED
        source.merged_into_id = target.id
        source.reviewed_by_id = reviewer_id
        source.reviewed_at = datetime.now(UTC)
        await session.commit()
        merged = await session.scalar(
            select(model).where(model.id == source.id).options(selectinload(model.aliases))
        )
        if merged is None:
            raise RuntimeError("Merged catalog could not be reloaded")
        return merged

    async def _transfer_aliases(
        self,
        session: AsyncSession,
        model: NamedCatalogModel,
        alias_model: NamedAliasModel,
        alias_foreign_key: str,
        source: NamedCatalog,
        target: NamedCatalog,
        label: str,
    ) -> None:
        names = [(source.name, source.normalized_name)]
        names.extend((alias.name, alias.normalized_name) for alias in source.aliases)
        for name, normalized_name in names:
            if normalized_name == target.normalized_name:
                continue
            canonical = await session.scalar(
                select(model).where(
                    model.normalized_name == normalized_name,
                    model.id.not_in([source.id, target.id]),
                )
            )
            existing_alias = await session.scalar(
                select(alias_model).where(alias_model.normalized_name == normalized_name)
            )
            if canonical is not None or (
                existing_alias is not None
                and getattr(existing_alias, alias_foreign_key) not in (source.id, target.id)
            ):
                raise ConflictError(f"Alias de {label.lower()} já está em uso")
            if existing_alias is not None:
                setattr(existing_alias, alias_foreign_key, target.id)
            else:
                session.add(
                    alias_model(
                        **{
                            alias_foreign_key: target.id,
                            "name": name,
                            "normalized_name": normalized_name,
                        }
                    )
                )


lead_service = LeadService()
