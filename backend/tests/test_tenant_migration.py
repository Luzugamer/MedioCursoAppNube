"""Exercise revision 0006 on a populated pre-tenant schema."""

from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text

from app.core.config import settings
from app.db.session import Base, engine
import app.models


def test_legacy_backfill_and_mismatch_guard():
    if not settings.DATABASE_URL.endswith("/siges_legacy"):
        pytest.skip("Only run migration test against siges_legacy")
    Base.metadata.create_all(engine)
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    with engine.begin() as connection:
        for table, constraints in {
            "clients": ["uq_clients_empresa_id"],
            "equipment": ["uq_equipment_empresa_id", "uq_equipment_empresa_cliente_id"],
            "services": ["uq_services_empresa_id", "uq_services_empresa_id_cliente"],
            "products": ["uq_products_empresa_id"],
            "users": ["uq_users_empresa_id"],
            "invoices": ["uq_invoices_empresa_id"],
        }.items():
            for name in constraints:
                connection.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {name}"))
        for table in ("service_items", "invoice_items"):
            connection.execute(text(f"ALTER TABLE {table} DROP COLUMN empresa_id CASCADE"))
        connection.execute(text("""
            INSERT INTO companies (id,nombre,activo,limite_usuarios,created_at,updated_at)
            VALUES (1001,'A',true,10,now(),now()), (1002,'B',true,10,now(),now())
        """))
        connection.execute(text("""
            INSERT INTO clients (id,empresa_id,nombres,apellidos,documento,telefono,activo,created_at)
            VALUES (1001,1001,'A','A','A-1001','123',true,now())
        """))
        connection.execute(text("""
            INSERT INTO products
              (id,empresa_id,nombre,categoria,codigo,stock,stock_minimo,precio_compra,precio_venta,activo,created_at)
            VALUES (1001,1001,'P','Otros','P-1001',5,1,1,2,true,now()),
                   (1002,1002,'P','Otros','P-1002',5,1,1,2,true,now())
        """))
        connection.execute(text("""
            INSERT INTO services
              (id,empresa_id,cliente_id,tipo_servicio,descripcion,estado,monto,fecha_ingreso,created_at,updated_at)
            VALUES (1001,1001,1001,'Test','Test','RECIBIDO',10,now(),now(),now())
        """))
        connection.execute(text("""
            INSERT INTO service_items
              (id,servicio_id,producto_id,cantidad,precio_unitario,subtotal,created_at)
            VALUES (1001,1001,1001,1,2,2,now()), (1002,1001,1002,1,2,2,now())
        """))
    command.stamp(config, "0005")
    with pytest.raises(RuntimeError, match="service item/product"):
        command.upgrade(config, "head")
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM service_items WHERE id=1002"))
    command.upgrade(config, "head")
    columns = {column["name"] for column in inspect(engine).get_columns("service_items")}
    assert "empresa_id" in columns
    with engine.connect() as connection:
        assert connection.execute(text("SELECT empresa_id FROM service_items WHERE id=1001")).scalar() == 1001
