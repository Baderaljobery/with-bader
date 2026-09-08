"""Safely adopt or apply the Alembic migration history.

An empty database is upgraded normally. A database created previously with
the manual 001-009 scripts is stamped only after Alembic confirms it matches
the complete SQLAlchemy metadata; no historical SQL is rerun on existing data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import inspect

import app.models  # noqa: F401
from app.database.base import Base
from app.database.session import engine

BASELINE_REVISION = "0001_legacy_009"
APPLICATION_TABLES = set(Base.metadata.tables)


def _config() -> Config:
    return Config("alembic.ini")


def main() -> None:
    config = _config()
    with engine.connect() as connection:
        tables = set(inspect(connection).get_table_names(schema="public"))
        has_version_table = "alembic_version" in tables
        existing_application_tables = tables & APPLICATION_TABLES

        if not has_version_table and existing_application_tables:
            if existing_application_tables != APPLICATION_TABLES:
                missing = sorted(APPLICATION_TABLES - existing_application_tables)
                raise RuntimeError(
                    "Refusing to stamp an incomplete legacy schema. Missing tables: "
                    + ", ".join(missing)
                )
            context = MigrationContext.configure(
                connection,
                opts={"compare_type": True, "compare_server_default": True},
            )
            # Revision 009 intentionally left this nullable. Head tightens
            # it in 0002 after an explicit ownerless-row guard.
            created_by = Base.metadata.tables["guests"].c.created_by
            head_nullable = created_by.nullable
            created_by.nullable = True
            try:
                differences = compare_metadata(context, Base.metadata)
            finally:
                created_by.nullable = head_nullable
            if differences:
                details = "\n".join(f"- {difference!r}" for difference in differences)
                raise RuntimeError(
                    "Refusing to stamp a legacy database with schema drift:\n" + details
                )

    if not has_version_table and existing_application_tables:
        command.stamp(config, BASELINE_REVISION)

    command.upgrade(config, "head")
    command.check(config)


if __name__ == "__main__":
    main()
