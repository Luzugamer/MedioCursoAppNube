"""Migrate before serving requests; never stamp an existing database at head."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.db.session import Base, engine
from app.db.init_db import init_db
import app.models  # Register every mapped table before create_all.


def main() -> None:
    config = Config(str(Path(__file__).resolve().parents[2] / "alembic.ini"))
    tables = set(inspect(engine).get_table_names())
    fresh = "companies" not in tables
    if fresh:
        if tables - {"alembic_version"}:
            raise RuntimeError("La base de datos contiene un esquema parcial; revise antes de iniciar")
        Base.metadata.create_all(bind=engine)
        command.stamp(config, "0005")
    elif "alembic_version" not in tables:
        required = {"companies", "users", "clients", "equipment", "services", "products", "invoices", "invoice_items", "service_items"}
        if not required.issubset(tables):
            raise RuntimeError("Esquema existente incompleto; no se puede registrar la versión inicial")
        command.stamp(config, "0005")
    command.upgrade(config, "head")
    init_db()


if __name__ == "__main__":
    main()
