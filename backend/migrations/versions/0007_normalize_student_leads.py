"""Normalize student lead academic data.

Revision ID: 0007_normalize_student_leads
Revises: 0006_student_leads
"""

import re
import unicodedata
import uuid
from typing import Sequence

import sqlalchemy as sa
from alembic import op
from fastapi_users_db_sqlalchemy.generics import GUID

revision: str = "0007_normalize_student_leads"
down_revision: str | Sequence[str] | None = "0006_student_leads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

catalog_namespace = uuid.UUID("8c7bc184-f3d8-41ec-adb7-246953ff9347")

institution_specs = (
    ("Universidade de São Paulo", ("USP",)),
    ("Universidade Estadual de Campinas", ("Unicamp",)),
    ("Universidade Estadual Paulista", ("Unesp",)),
    ("Universidade Federal do Rio de Janeiro", ("UFRJ",)),
    ("Universidade Federal de Minas Gerais", ("UFMG",)),
    ("Universidade de Brasília", ("UnB",)),
    ("Universidade Federal do Paraná", ("UFPR",)),
    ("Universidade Federal do Rio Grande do Sul", ("UFRGS",)),
    ("Universidade Federal de Santa Catarina", ("UFSC",)),
    ("Universidade Federal de Pernambuco", ("UFPE",)),
    ("Universidade Federal do Ceará", ("UFC",)),
    ("Universidade Federal da Bahia", ("UFBA",)),
    ("Universidade Federal do Pará", ("UFPA",)),
    ("Universidade Federal do Amazonas", ("UFAM",)),
    ("Universidade Federal de Goiás", ("UFG",)),
    ("Universidade Federal de Mato Grosso do Sul", ("UFMS",)),
    ("Universidade Federal de São Carlos", ("UFSCar",)),
    ("Universidade Tecnológica Federal do Paraná", ("UTFPR",)),
    ("Instituto Federal de São Paulo", ("IFSP",)),
    ("Faculdade de Tecnologia de Jacareí", ("Fatec Jacareí",)),
    ("Pontifícia Universidade Católica de São Paulo", ("PUC-SP",)),
    ("Universidade Presbiteriana Mackenzie", ("Mackenzie",)),
)

course_specs = (
    ("Análise e Desenvolvimento de Sistemas", ("ADS",)),
    ("Desenvolvimento de Software Multiplataforma", ("DSM",)),
    ("Ciência da Computação", ("CC", "Ciências da Computação")),
    ("Sistemas de Informação", ("SI",)),
    ("Engenharia de Software", ()),
    ("Engenharia de Dados", ()),
    ("Engenharia da Computação", ()),
    ("Banco de Dados", ()),
    ("Ciência de Dados", ()),
    ("Inteligência Artificial", ("IA",)),
    ("Segurança da Informação", ()),
    ("Redes de Computadores", ()),
)

interest_area_specs = (
    ("backend", "Backend"),
    ("frontend", "Frontend"),
    ("mobile", "Desenvolvimento mobile"),
    ("data", "Dados e analytics"),
    ("devops-cloud", "DevOps e cloud"),
    ("ai", "Inteligência artificial"),
    ("cybersecurity", "Cibersegurança"),
    ("product", "Produto"),
    ("ux-ui", "UX e UI"),
    ("qa", "Qualidade de software"),
    ("entrepreneurship", "Empreendedorismo"),
)

legacy_interest_codes = {
    "backend": "backend",
    "frontend": "frontend",
    "devops": "devops-cloud",
    "produto": "product",
    "ux ui": "ux-ui",
}


def normalize_name(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    alphanumeric = re.sub(r"[^a-z0-9]+", " ", without_accents.casefold())
    return " ".join(alphanumeric.split())


def stable_id(kind: str, key: str) -> uuid.UUID:
    return uuid.uuid5(catalog_namespace, f"{kind}:{key}")


def timestamp_column(name: str) -> sa.Column:
    return sa.Column(
        name,
        sa.DateTime(timezone=True),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        nullable=False,
    )


def create_catalog_tables() -> tuple[sa.Table, sa.Table, sa.Table, sa.Table, sa.Table]:
    institutions = op.create_table(
        "educational_institutions",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("merged_into_id", GUID(), nullable=True),
        sa.Column("reviewed_by_id", GUID(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'merged')",
            name="ck_educational_institutions_status",
        ),
        sa.CheckConstraint(
            "merged_into_id IS NULL OR merged_into_id <> id",
            name="ck_educational_institutions_not_self_merged",
        ),
        sa.ForeignKeyConstraint(
            ["merged_into_id"], ["educational_institutions.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_index("ix_educational_institutions_status", "educational_institutions", ["status"])

    institution_aliases = op.create_table(
        "educational_institution_aliases",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("institution_id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["educational_institutions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_index(
        "ix_educational_institution_aliases_institution_id",
        "educational_institution_aliases",
        ["institution_id"],
    )

    courses = op.create_table(
        "academic_courses",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("merged_into_id", GUID(), nullable=True),
        sa.Column("reviewed_by_id", GUID(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'merged')", name="ck_academic_courses_status"
        ),
        sa.CheckConstraint(
            "merged_into_id IS NULL OR merged_into_id <> id",
            name="ck_academic_courses_not_self_merged",
        ),
        sa.ForeignKeyConstraint(["merged_into_id"], ["academic_courses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_index("ix_academic_courses_status", "academic_courses", ["status"])

    course_aliases = op.create_table(
        "academic_course_aliases",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("course_id", GUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("normalized_name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["academic_courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("normalized_name"),
    )
    op.create_index(
        "ix_academic_course_aliases_course_id", "academic_course_aliases", ["course_id"]
    )

    interest_areas = op.create_table(
        "interest_areas",
        sa.Column("id", GUID(), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true(), nullable=False),
        timestamp_column("created_at"),
        timestamp_column("updated_at"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_interest_areas_active", "interest_areas", ["active"])
    return institutions, institution_aliases, courses, course_aliases, interest_areas


def seed_named_catalog(
    bind,
    table: sa.Table,
    alias_table: sa.Table,
    kind: str,
    foreign_key: str,
    specs: tuple,
) -> dict[str, uuid.UUID]:
    lookup: dict[str, uuid.UUID] = {}
    rows = []
    aliases = []
    for name, item_aliases in specs:
        normalized = normalize_name(name)
        item_id = stable_id(kind, normalized)
        rows.append(
            {"id": item_id, "name": name, "normalized_name": normalized, "status": "approved"}
        )
        lookup[normalized] = item_id
        for alias in item_aliases:
            normalized_alias = normalize_name(alias)
            lookup[normalized_alias] = item_id
            aliases.append(
                {
                    "id": stable_id(f"{kind}-alias", normalized_alias),
                    foreign_key: item_id,
                    "name": alias,
                    "normalized_name": normalized_alias,
                }
            )
    bind.execute(sa.insert(table), rows)
    if aliases:
        bind.execute(sa.insert(alias_table), aliases)
    return lookup


def seed_interest_areas(bind, table: sa.Table) -> dict[str, uuid.UUID]:
    rows = []
    by_code = {}
    for code, name in interest_area_specs:
        item_id = stable_id("interest-area", code)
        rows.append({"id": item_id, "code": code, "name": name, "active": True})
        by_code[code] = item_id
    bind.execute(sa.insert(table), rows)
    return by_code


def parse_semester(value: str | None) -> int | None:
    numbers = re.findall(r"\d+", value or "")
    if len(numbers) != 1:
        return None
    semester = int(numbers[0])
    return semester if 1 <= semester <= 12 else None


def backfill_student_leads(
    bind,
    institutions: sa.Table,
    courses: sa.Table,
    institution_lookup: dict[str, uuid.UUID],
    course_lookup: dict[str, uuid.UUID],
    area_ids: dict[str, uuid.UUID],
) -> None:
    leads = sa.table(
        "leads",
        sa.column("id", GUID()),
        sa.column("lead_type", sa.String()),
        sa.column("institution_name", sa.String()),
        sa.column("course_name", sa.String()),
        sa.column("semester", sa.String()),
        sa.column("area_of_interest", sa.String()),
        sa.column("institution_id", GUID()),
        sa.column("course_id", GUID()),
        sa.column("semester_number", sa.Integer()),
    )
    lead_areas = sa.table(
        "lead_interest_areas",
        sa.column("lead_id", GUID()),
        sa.column("interest_area_id", GUID()),
    )

    rows = bind.execute(
        sa.select(
            leads.c.id,
            leads.c.institution_name,
            leads.c.course_name,
            leads.c.semester,
            leads.c.area_of_interest,
        ).where(leads.c.lead_type == "student")
    )
    for row in rows:
        values = row._mapping
        normalized_institution = normalize_name(values["institution_name"] or "")
        institution_id = institution_lookup.get(normalized_institution)
        if institution_id is None and normalized_institution:
            institution_id = stable_id("backfill-institution", normalized_institution)
            bind.execute(
                sa.insert(institutions).values(
                    id=institution_id,
                    name=values["institution_name"].strip(),
                    normalized_name=normalized_institution,
                    status="pending",
                )
            )
            institution_lookup[normalized_institution] = institution_id

        normalized_course = normalize_name(values["course_name"] or "")
        course_id = course_lookup.get(normalized_course)
        if course_id is None and normalized_course:
            course_id = stable_id("backfill-course", normalized_course)
            bind.execute(
                sa.insert(courses).values(
                    id=course_id,
                    name=values["course_name"].strip(),
                    normalized_name=normalized_course,
                    status="pending",
                )
            )
            course_lookup[normalized_course] = course_id

        bind.execute(
            sa.update(leads)
            .where(leads.c.id == values["id"])
            .values(
                institution_id=institution_id,
                course_id=course_id,
                semester_number=parse_semester(values["semester"]),
            )
        )

        legacy_area = normalize_name(values["area_of_interest"] or "")
        area_code = legacy_interest_codes.get(legacy_area)
        if area_code is not None:
            bind.execute(
                sa.insert(lead_areas).values(
                    lead_id=values["id"], interest_area_id=area_ids[area_code]
                )
            )


def upgrade() -> None:
    institutions, institution_aliases, courses, course_aliases, interest_areas = (
        create_catalog_tables()
    )

    recreate = "always" if op.get_context().dialect.name == "sqlite" else "auto"
    with op.batch_alter_table("leads", recreate=recreate) as batch_op:
        batch_op.add_column(sa.Column("institution_id", GUID(), nullable=True))
        batch_op.add_column(sa.Column("course_id", GUID(), nullable=True))
        batch_op.add_column(sa.Column("semester_number", sa.Integer(), nullable=True))
        batch_op.create_index("ix_leads_institution_id", ["institution_id"])
        batch_op.create_index("ix_leads_course_id", ["course_id"])
        batch_op.create_index("ix_leads_semester_number", ["semester_number"])
        batch_op.create_check_constraint(
            "ck_leads_semester_number",
            "semester_number IS NULL OR semester_number BETWEEN 1 AND 12",
        )
        batch_op.create_foreign_key(
            "fk_leads_institution_id_educational_institutions",
            "educational_institutions",
            ["institution_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        batch_op.create_foreign_key(
            "fk_leads_course_id_academic_courses",
            "academic_courses",
            ["course_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    op.create_table(
        "lead_interest_areas",
        sa.Column("lead_id", GUID(), nullable=False),
        sa.Column("interest_area_id", GUID(), nullable=False),
        timestamp_column("created_at"),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interest_area_id"], ["interest_areas.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("lead_id", "interest_area_id"),
    )
    op.create_index(
        "ix_lead_interest_areas_interest_area_id",
        "lead_interest_areas",
        ["interest_area_id"],
    )

    bind = op.get_bind()
    institution_lookup = seed_named_catalog(
        bind,
        institutions,
        institution_aliases,
        "institution",
        "institution_id",
        institution_specs,
    )
    course_lookup = seed_named_catalog(
        bind, courses, course_aliases, "course", "course_id", course_specs
    )
    area_ids = seed_interest_areas(bind, interest_areas)
    backfill_student_leads(
        bind,
        institutions,
        courses,
        institution_lookup,
        course_lookup,
        area_ids,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_interest_areas_interest_area_id", table_name="lead_interest_areas")
    op.drop_table("lead_interest_areas")

    recreate = "always" if op.get_context().dialect.name == "sqlite" else "auto"
    with op.batch_alter_table("leads", recreate=recreate) as batch_op:
        batch_op.drop_constraint("fk_leads_course_id_academic_courses", type_="foreignkey")
        batch_op.drop_constraint(
            "fk_leads_institution_id_educational_institutions", type_="foreignkey"
        )
        batch_op.drop_constraint("ck_leads_semester_number", type_="check")
        batch_op.drop_index("ix_leads_semester_number")
        batch_op.drop_index("ix_leads_course_id")
        batch_op.drop_index("ix_leads_institution_id")
        batch_op.drop_column("semester_number")
        batch_op.drop_column("course_id")
        batch_op.drop_column("institution_id")

    op.drop_index("ix_interest_areas_active", table_name="interest_areas")
    op.drop_table("interest_areas")
    op.drop_index("ix_academic_course_aliases_course_id", table_name="academic_course_aliases")
    op.drop_table("academic_course_aliases")
    op.drop_index("ix_academic_courses_status", table_name="academic_courses")
    op.drop_table("academic_courses")
    op.drop_index(
        "ix_educational_institution_aliases_institution_id",
        table_name="educational_institution_aliases",
    )
    op.drop_table("educational_institution_aliases")
    op.drop_index("ix_educational_institutions_status", table_name="educational_institutions")
    op.drop_table("educational_institutions")
