import os
import sqlite3
import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).parents[1]


def run_alembic(database: Path, *arguments: str) -> None:
    environment = {
        **os.environ,
        "DATABASE_URL": f"sqlite+aiosqlite:///{database}",
    }
    subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=BACKEND_ROOT,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def test_normalization_migration_backfills_and_preserves_legacy_data(tmp_path: Path) -> None:
    database = tmp_path / "student-leads.db"
    run_alembic(database, "upgrade", "0006_student_leads")

    with sqlite3.connect(database) as connection:
        connection.executemany(
            """
            INSERT INTO leads (
                id, full_name, email, company_name, privacy_consent, source, lead_type,
                institution_name, course_name, semester, area_of_interest
            ) VALUES (?, ?, ?, NULL, 1, 'migration-test', 'student', ?, ?, ?, ?)
            """,
            [
                (
                    "11111111-1111-1111-1111-111111111111",
                    "Ada Lovelace",
                    "ada@example.com",
                    " fatec JACAREÍ ",
                    "ADS",
                    "4º semestre",
                    "Backend",
                ),
                (
                    "22222222-2222-2222-2222-222222222222",
                    "Grace Hopper",
                    "grace@example.com",
                    "Instituto Desconhecido",
                    "Curso Desconhecido",
                    "período 2 de 8",
                    "Aeroespacial",
                ),
            ],
        )

    run_alembic(database, "upgrade", "head")
    with sqlite3.connect(database) as connection:
        leads = connection.execute(
            """
            SELECT institution_name, course_name, semester, area_of_interest,
                   semester_number, institution_id IS NOT NULL, course_id IS NOT NULL
            FROM leads ORDER BY email
            """
        ).fetchall()
        pending_institutions = connection.execute(
            "SELECT name FROM educational_institutions WHERE status = 'pending'"
        ).fetchall()
        pending_courses = connection.execute(
            "SELECT name FROM academic_courses WHERE status = 'pending'"
        ).fetchall()
        area_links = connection.execute("SELECT count(*) FROM lead_interest_areas").fetchone()[0]

    assert leads == [
        (" fatec JACAREÍ ", "ADS", "4º semestre", "Backend", 4, 1, 1),
        (
            "Instituto Desconhecido",
            "Curso Desconhecido",
            "período 2 de 8",
            "Aeroespacial",
            None,
            1,
            1,
        ),
    ]
    assert pending_institutions == [("Instituto Desconhecido",)]
    assert pending_courses == [("Curso Desconhecido",)]
    assert area_links == 1

    run_alembic(database, "downgrade", "0006_student_leads")
    with sqlite3.connect(database) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(leads)")}
        legacy = connection.execute(
            "SELECT institution_name, course_name FROM leads ORDER BY email"
        ).fetchall()
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }

    assert "institution_id" not in columns
    assert "educational_institutions" not in tables
    assert legacy[1] == ("Instituto Desconhecido", "Curso Desconhecido")

    run_alembic(database, "upgrade", "head")
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT count(*) FROM educational_institutions WHERE status = 'pending'"
        ).fetchone() == (1,)
