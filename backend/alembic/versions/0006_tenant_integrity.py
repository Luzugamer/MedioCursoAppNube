"""Enforce shared-table tenant ownership and cross-module integrity.

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

UNIQUE_KEYS = {
    "clients": [("uq_clients_empresa_id", "empresa_id, id")],
    "equipment": [
        ("uq_equipment_empresa_id", "empresa_id, id"),
        ("uq_equipment_empresa_cliente_id", "empresa_id, cliente_id, id"),
    ],
    "services": [
        ("uq_services_empresa_id", "empresa_id, id"),
        ("uq_services_empresa_id_cliente", "empresa_id, id, cliente_id"),
    ],
    "products": [("uq_products_empresa_id", "empresa_id, id")],
    "users": [("uq_users_empresa_id", "empresa_id, id")],
    "invoices": [("uq_invoices_empresa_id", "empresa_id, id")],
}

FOREIGN_KEYS = {
    "equipment": [
        ("fk_equipment_client_tenant", "(empresa_id, cliente_id) REFERENCES clients (empresa_id, id) ON DELETE CASCADE"),
    ],
    "services": [
        ("fk_services_client_tenant", "(empresa_id, cliente_id) REFERENCES clients (empresa_id, id) ON DELETE CASCADE"),
        ("fk_services_equipment_client_tenant", "(empresa_id, cliente_id, equipo_id) REFERENCES equipment (empresa_id, cliente_id, id) ON DELETE SET NULL (equipo_id)"),
        ("fk_services_responsible_tenant", "(empresa_id, usuario_responsable_id) REFERENCES users (empresa_id, id) ON DELETE SET NULL (usuario_responsable_id)"),
    ],
    "inventory_movements": [
        ("fk_movements_product_tenant", "(empresa_id, producto_id) REFERENCES products (empresa_id, id) ON DELETE CASCADE"),
        ("fk_movements_service_tenant", "(empresa_id, servicio_id) REFERENCES services (empresa_id, id) ON DELETE SET NULL (servicio_id)"),
    ],
    "payments": [
        ("fk_payments_service_tenant", "(empresa_id, servicio_id) REFERENCES services (empresa_id, id) ON DELETE CASCADE"),
    ],
    "invoices": [
        ("fk_invoices_service_client_tenant", "(empresa_id, servicio_id, cliente_id) REFERENCES services (empresa_id, id, cliente_id)"),
    ],
    "licenses": [
        ("fk_licenses_client_tenant", "(empresa_id, cliente_id) REFERENCES clients (empresa_id, id) ON DELETE SET NULL (cliente_id)"),
        ("fk_licenses_equipment_tenant", "(empresa_id, equipo_id) REFERENCES equipment (empresa_id, id) ON DELETE SET NULL (equipo_id)"),
    ],
    "notifications": [
        ("fk_notifications_client_tenant", "(empresa_id, cliente_id) REFERENCES clients (empresa_id, id) ON DELETE CASCADE"),
        ("fk_notifications_service_client_tenant", "(empresa_id, servicio_id, cliente_id) REFERENCES services (empresa_id, id, cliente_id) ON DELETE CASCADE"),
    ],
    "service_items": [
        ("fk_service_items_company", "(empresa_id) REFERENCES companies (id) ON DELETE CASCADE"),
        ("fk_service_items_service_tenant", "(empresa_id, servicio_id) REFERENCES services (empresa_id, id) ON DELETE CASCADE"),
        ("fk_service_items_product_tenant", "(empresa_id, producto_id) REFERENCES products (empresa_id, id)"),
    ],
    "invoice_items": [
        ("fk_invoice_items_company", "(empresa_id) REFERENCES companies (id) ON DELETE CASCADE"),
        ("fk_invoice_items_invoice_tenant", "(empresa_id, comprobante_id) REFERENCES invoices (empresa_id, id) ON DELETE CASCADE"),
        ("fk_invoice_items_product_tenant", "(empresa_id, producto_id) REFERENCES products (empresa_id, id)"),
    ],
}

REFERENCES = [
    ("equipment", "cliente_id", "clients"),
    ("services", "cliente_id", "clients"),
    ("services", "equipo_id", "equipment"),
    ("services", "usuario_responsable_id", "users"),
    ("inventory_movements", "producto_id", "products"),
    ("inventory_movements", "servicio_id", "services"),
    ("payments", "servicio_id", "services"),
    ("invoices", "servicio_id", "services"),
    ("invoices", "cliente_id", "clients"),
    ("licenses", "cliente_id", "clients"),
    ("licenses", "equipo_id", "equipment"),
    ("notifications", "cliente_id", "clients"),
    ("notifications", "servicio_id", "services"),
]


def _constraint_exists(table: str, name: str) -> bool:
    return bool(op.get_bind().execute(sa.text(
        "SELECT 1 FROM pg_constraint WHERE conrelid = to_regclass(:table) AND conname = :name"
    ), {"table": table, "name": name}).scalar())


def _validate_existing_rows() -> None:
    connection = op.get_bind()
    for child, column, parent in REFERENCES:
        # Global superadministrators may be actors, but not assigned technicians.
        query = f"""SELECT c.id FROM {child} c JOIN {parent} p ON p.id = c.{column}
                    WHERE c.{column} IS NOT NULL AND c.empresa_id IS DISTINCT FROM p.empresa_id
                    LIMIT 1"""
        if connection.execute(sa.text(query)).first():
            raise RuntimeError(f"Datos incompatibles: {child}.{column} apunta a otra empresa")
    checks = {
        "service equipment/client": "SELECT s.id FROM services s JOIN equipment e ON e.id=s.equipo_id WHERE s.cliente_id<>e.cliente_id LIMIT 1",
        "invoice service/client": "SELECT i.id FROM invoices i JOIN services s ON s.id=i.servicio_id WHERE i.cliente_id<>s.cliente_id LIMIT 1",
        "notification service/client": "SELECT n.id FROM notifications n JOIN services s ON s.id=n.servicio_id WHERE n.cliente_id<>s.cliente_id LIMIT 1",
        "service item/product": "SELECT si.id FROM service_items si JOIN services s ON s.id=si.servicio_id JOIN products p ON p.id=si.producto_id WHERE s.empresa_id<>p.empresa_id LIMIT 1",
        "invoice item/product": "SELECT ii.id FROM invoice_items ii JOIN invoices i ON i.id=ii.comprobante_id JOIN products p ON p.id=ii.producto_id WHERE i.empresa_id<>p.empresa_id LIMIT 1",
        "license equipment/client": "SELECT l.id FROM licenses l JOIN equipment e ON e.id=l.equipo_id WHERE l.cliente_id IS NOT NULL AND l.cliente_id<>e.cliente_id LIMIT 1",
        "tenant roles": "SELECT u.id FROM users u JOIN roles r ON r.id=u.rol_id WHERE (r.nombre='SUPERADMIN' AND u.empresa_id IS NOT NULL) OR (r.nombre<>'SUPERADMIN' AND u.empresa_id IS NULL) LIMIT 1",
    }
    for label, query in checks.items():
        if connection.execute(sa.text(query)).first():
            raise RuntimeError(f"Datos incompatibles: {label}")


def upgrade() -> None:
    _validate_existing_rows()
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    for table, parent, parent_key in (
        ("service_items", "services", "servicio_id"),
        ("invoice_items", "invoices", "comprobante_id"),
    ):
        if "empresa_id" not in {column["name"] for column in inspector.get_columns(table)}:
            op.add_column(table, sa.Column("empresa_id", sa.Integer(), nullable=True))
        op.execute(f"UPDATE {table} d SET empresa_id = p.empresa_id FROM {parent} p WHERE p.id = d.{parent_key} AND d.empresa_id IS NULL")
        missing = connection.execute(sa.text(f"SELECT id FROM {table} WHERE empresa_id IS NULL LIMIT 1")).first()
        if missing:
            raise RuntimeError(f"No se pudo determinar empresa_id en {table}")
        op.alter_column(table, "empresa_id", nullable=False)
        index = f"ix_{table}_empresa_id"
        if index not in {item["name"] for item in inspector.get_indexes(table)}:
            op.create_index(index, table, ["empresa_id"])

    op.execute("UPDATE audit_logs a SET empresa_id=u.empresa_id FROM users u WHERE a.usuario_id=u.id AND a.empresa_id IS NULL AND u.empresa_id IS NOT NULL")
    for table in ("payments", "invoices", "inventory_movements", "audit_logs"):
        mismatch = connection.execute(sa.text(f"""
            SELECT c.id FROM {table} c
            JOIN users u ON u.id = c.usuario_id JOIN roles r ON r.id = u.rol_id
            WHERE c.usuario_id IS NOT NULL
              AND NOT (u.empresa_id IS NOT DISTINCT FROM c.empresa_id
                       OR (u.empresa_id IS NULL AND r.nombre = 'SUPERADMIN'))
            LIMIT 1
        """)).first()
        if mismatch:
            raise RuntimeError(f"Autor de otra empresa en {table}; corrija antes de migrar")
    for table, definitions in UNIQUE_KEYS.items():
        for name, columns in definitions:
            if not _constraint_exists(table, name):
                op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} UNIQUE ({columns})")
    for table, definitions in FOREIGN_KEYS.items():
        for name, definition in definitions:
            if not _constraint_exists(table, name):
                op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} FOREIGN KEY {definition}")
    op.execute("""
        CREATE OR REPLACE FUNCTION check_tenant_actor() RETURNS trigger AS $$
        DECLARE actor_company integer; actor_role text;
        BEGIN
            SELECT u.empresa_id, r.nombre INTO actor_company, actor_role
            FROM users u JOIN roles r ON r.id = u.rol_id WHERE u.id = NEW.usuario_id;
            IF NOT FOUND OR NOT (
                actor_company IS NOT DISTINCT FROM NEW.empresa_id
                OR (actor_company IS NULL AND actor_role = 'SUPERADMIN')
            ) THEN
                RAISE EXCEPTION 'Autor de otra empresa en %', TG_TABLE_NAME;
            END IF;
            RETURN NEW;
        END; $$ LANGUAGE plpgsql;
    """)
    for table in ("payments", "invoices", "inventory_movements", "audit_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_actor_tenant ON {table}")
        op.execute(f"CREATE TRIGGER trg_{table}_actor_tenant BEFORE INSERT OR UPDATE OF empresa_id, usuario_id ON {table} FOR EACH ROW WHEN (NEW.usuario_id IS NOT NULL) EXECUTE FUNCTION check_tenant_actor()")
    op.execute("""
        CREATE OR REPLACE FUNCTION check_user_tenant_role() RETURNS trigger AS $$
        DECLARE role_name text;
        BEGIN
            SELECT nombre INTO role_name FROM roles WHERE id = NEW.rol_id;
            IF (role_name = 'SUPERADMIN') <> (NEW.empresa_id IS NULL) THEN
                RAISE EXCEPTION 'Rol incompatible con empresa';
            END IF;
            IF TG_OP = 'UPDATE' AND NEW.empresa_id IS DISTINCT FROM OLD.empresa_id THEN
                RAISE EXCEPTION 'La empresa de un usuario no se puede cambiar';
            END IF;
            RETURN NEW;
        END; $$ LANGUAGE plpgsql;
    """)
    op.execute("DROP TRIGGER IF EXISTS trg_users_tenant_role ON users")
    op.execute("CREATE TRIGGER trg_users_tenant_role BEFORE INSERT OR UPDATE OF empresa_id, rol_id ON users FOR EACH ROW EXECUTE FUNCTION check_user_tenant_role()")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_users_tenant_role ON users")
    op.execute("DROP FUNCTION IF EXISTS check_user_tenant_role()")
    for table in ("payments", "invoices", "inventory_movements", "audit_logs"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_actor_tenant ON {table}")
    op.execute("DROP FUNCTION IF EXISTS check_tenant_actor()")
    for table, definitions in reversed(list(FOREIGN_KEYS.items())):
        for name, _ in definitions:
            if _constraint_exists(table, name):
                op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {name}")
    for table, definitions in reversed(list(UNIQUE_KEYS.items())):
        for name, _ in definitions:
            if _constraint_exists(table, name):
                op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {name}")
    for table in ("invoice_items", "service_items"):
        op.drop_column(table, "empresa_id")
