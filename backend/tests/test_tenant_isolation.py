"""Integration checks against an isolated PostgreSQL database named siges_test."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.session import SessionLocal
from app.main import app
from app.api.routes.uploads import upload_sessions


@pytest.fixture(scope="module")
def client():
    if not settings.DATABASE_URL.endswith("/siges_test"):
        pytest.skip("Only run tenant integration tests against siges_test")
    return TestClient(app)


def _login(client, email, password):
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _new_company(client, super_headers, suffix):
    email = f"admin-{suffix}@example.com"
    response = client.post("/api/companies/", headers=super_headers, json={
        "nombre": f"Empresa {suffix}", "admin_nombre": "Administrador",
        "admin_email": email, "admin_password": "Password123!",
    })
    assert response.status_code == 201, response.text
    return response.json()["id"], _login(client, email, "Password123!")


def test_isolation_across_api_database_pdf_and_qr(client):
    suffix = uuid4().hex[:10]
    super_headers = _login(client, "superadmin@sistec.com", "SuperAdmin123!")
    company_a, headers_a = _new_company(client, super_headers, f"a-{suffix}")
    company_b, headers_b = _new_company(client, super_headers, f"b-{suffix}")

    assert client.post("/api/clients/", headers=super_headers, json={
        "nombres": "Sin", "apellidos": "Empresa", "documento": suffix,
        "telefono": "123456789",
    }).status_code == 422

    def new_client(headers, document):
        response = client.post("/api/clients/", headers=headers, json={
            "nombres": "Cliente", "apellidos": "Prueba", "documento": document,
            "telefono": "123456789",
        })
        assert response.status_code == 201, response.text
        return response.json()["id"]

    client_a = new_client(headers_a, f"A-{suffix}")
    client_b = new_client(headers_b, f"B-{suffix}")
    admin_b = next(row["id"] for row in client.get(
        f"/api/users/?empresa_id={company_b}", headers=super_headers,
    ).json() if row["email"].startswith("admin-b-"))
    assert client.post("/api/services/", headers=headers_a, json={
        "cliente_id": client_a, "tipo_servicio": "Reparación",
        "descripcion": "Responsable externo", "usuario_responsable_id": admin_b,
    }).status_code == 400
    superadmin_role = next(row["id"] for row in client.get(
        "/api/users/roles", headers=super_headers,
    ).json() if row["nombre"] == "SUPERADMIN")
    assert client.post("/api/users/", headers=headers_b, json={
        "nombre": "Escalada", "email": f"escalada-{suffix}@example.com",
        "password": "Password123!", "rol_id": superadmin_role,
    }).status_code == 403
    assert client.post("/api/equipment/", headers=headers_b, json={
        "cliente_id": client_a, "tipo": "Laptop", "marca": "Marca", "modelo": "Modelo",
    }).status_code == 404

    service_response = client.post("/api/services/", headers=headers_a, json={
        "cliente_id": client_a, "tipo_servicio": "Reparación",
        "descripcion": "Prueba de aislamiento", "monto": 50,
    })
    assert service_response.status_code == 201, service_response.text
    service_a = service_response.json()["id"]
    assert client.get(f"/api/services/{service_a}", headers=headers_b).status_code == 404
    assert client.post("/api/payments/", headers=headers_b, json={
        "servicio_id": service_a, "monto": 10, "metodo_pago": "EFECTIVO",
    }).status_code == 404

    invoice_response = client.post("/api/invoices/", headers=headers_a, json={
        "servicio_id": service_a, "tipo_comprobante": "BOLETA", "serie": "B001",
    })
    assert invoice_response.status_code == 201, invoice_response.text
    invoice_a = invoice_response.json()["id"]
    assert client.get(f"/api/invoices/{invoice_a}", headers=headers_b).status_code == 404
    assert client.get(f"/api/invoices/{invoice_a}/pdf", headers=headers_b).status_code == 404
    assert client.get(f"/api/invoices/{invoice_a}/pdf", headers=headers_a).status_code == 200

    product = client.post("/api/products/", headers=headers_b, json={
        "nombre": "Repuesto", "categoria": "Otros", "codigo": f"P-{suffix}",
        "stock": 5, "precio_compra": 1, "precio_venta": 2,
    })
    assert product.status_code == 201, product.text
    product_b = product.json()["id"]
    assert client.post(f"/api/services/{service_a}/products", headers=headers_a, json={
        "producto_id": product_b, "cantidad": 1,
    }).status_code == 404

    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            db.execute(text("""
                INSERT INTO service_items
                  (empresa_id, servicio_id, producto_id, cantidad, precio_unitario, subtotal, created_at)
                VALUES (:company, :service, :product, 1, 2, 2, now())
            """), {"company": company_a, "service": service_a, "product": product_b})
            db.commit()
        db.rollback()
        with pytest.raises(IntegrityError):
            db.execute(text("""
                INSERT INTO equipment
                  (empresa_id, cliente_id, tipo, marca, modelo, created_at)
                VALUES (:company, :client, 'Laptop', 'Marca', 'Modelo', now())
            """), {"company": company_b, "client": client_a})
            db.commit()
        db.rollback()

    assert any(row["id"] == client_a for row in client.get("/api/clients/", headers=super_headers).json())
    assert all(row["empresa_id"] == company_b for row in client.get(
        f"/api/clients/?empresa_id={company_b}", headers=super_headers,
    ).json())
    assert client.post("/api/clients/", headers=headers_a, json={
        "empresa_id": company_b, "nombres": "No", "apellidos": "Permitido",
        "documento": f"X-{suffix}", "telefono": "123456789",
    }).status_code == 403

    image = client.post("/api/uploads/file", headers=headers_a, files={
        "file": ("photo.png", b"\x89PNG\r\n\x1a\nimage", "image/png"),
    })
    assert image.status_code == 200, image.text
    image_url = image.json()["url"]
    assert image_url.startswith(f"/static/uploads/{company_a}/")
    assert client.get(image_url).status_code == 200  # Public by design.
    assert client.post("/api/equipment/", headers=headers_b, json={
        "cliente_id": client_b, "tipo": "Laptop", "marca": "Marca",
        "modelo": "Modelo", "imagen_url": image_url,
    }).status_code == 400

    session = client.post("/api/uploads/session/create", headers=headers_a).json()
    session_id = session["session_id"]
    assert client.get(f"/api/uploads/session/{session_id}", headers=headers_b).status_code == 404
    capture = client.post(f"/api/uploads/session/{session_id}/upload", files={
        "file": ("camera.jpg", b"\xff\xd8\xffimage", "image/jpeg"),
    })
    assert capture.status_code == 200, capture.text
    assert client.post(f"/api/uploads/session/{session_id}/upload", files={
        "file": ("camera.jpg", b"\xff\xd8\xffimage", "image/jpeg"),
    }).status_code == 409
    assert client.get(f"/api/uploads/session/{session_id}", headers=headers_a).json()["status"] == "COMPLETED"
    upload_sessions[session_id]["expires_at"] = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert client.get(f"/api/uploads/session/{session_id}", headers=headers_a).status_code == 410
