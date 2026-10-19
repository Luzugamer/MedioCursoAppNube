# Trazabilidad y control de cobertura

## Método y alcance

Fecha: 2026-10-13 (America/Lima). Se partió de exploración recursiva de código propio y configuración; se revisaron puntos de entrada, handlers, schemas, modelos, servicios auxiliares y llamadores React; después se contrastaron contratos, migraciones y documentación. Las páginas se revisaron por lógica, transformaciones, condiciones y enlaces de UI; no se evaluó su apariencia ejecutada. Los manifiestos se analizaron sin abrir código de terceros.

Estados usados: **pendiente** (sin inspección), **en análisis** (recorrido parcial), **documentado** (descrito), **verificado** (contrastado con sus dependencias propias, estáticamente). El inventario comenzó pendiente y quedó verificado para texto; los dos JPG solo están documentados por metadata. Esto no certifica funcionamiento de la instancia.

Exclusiones: `.env*` (archivos y directorios), node_modules, vendor, .venv/venv, __pycache__, .git, .agents/.codex/.aws, dist/build/bin/obj y contenido de uploads binarios. No se importó app, se ejecutaron migraciones/tests ni se contactaron servicios. La ausencia de Git utilizable impide un diff de commit; se conservaron SHA-256 iniciales y se compararon al cierre.

## Progreso por fases

| Fase | Estado de análisis estático | Entregables |
|---|---|---|
| 1. Reconocimiento | Verificado | 00, 01, inventario.json |
| 2. Funcionalidades | Verificado | 03, rutas y dependencias en 06 |
| 3. Arquitectura | Verificado | 02, diagramas componentes/dependencias |
| 4. Datos | Verificado | 04, 05, contratos de 06 |
| 5. Flujos | Verificado | 07, diagramas de secuencia/flujo |
| 6. Centralización | Verificado | 12 Markdown solicitados y anexos |
| 7. Trazabilidad | Verificado | Referencias a fuente, hashes, contraste OpenAPI |
| 8. Cobertura | Verificado | Matrices siguientes y verificacion.md |

## Inventario de módulos y funcionalidades

| ID | Módulo | Estado | Archivos/grupos inspeccionados | Dependencias recorridas | Evidencias/documentación | Pendientes o límites |
|---|---|---|---|---|---|---|
| F01 | Identidad y sesión | Verificado estático | auth, security, deps, AuthContext, api, Login | User/Role/Company; JWT/bcrypt; Audit; localStorage | 03 F01; 02; 06 | U01/U02/U03 |
| F02 | Empresas | Verificado estático | companies y Superadmin; model/schema company | User/Role; hashing; Audit; cupo | 03 F02; R07/R11/R12; H02/H04 | U02; transacción parcial H27 |
| F03 | Usuarios, roles y permisos | Verificado estático | users, role, schemas, permissions, Users | Company; bcrypt; Audit; controles HTTP/UI | 03 F03; 04; H02/H06/H19 | U02/U03 |
| F04 | Clientes | Verificado estático | clients, model/schema client, Clients | Company; Audit; equipos/servicios/licencias/pagos | 03 F04; H13/H20 | U02/U03 |
| F05 | Equipos | Verificado estático | equipment, model/schema, Equipment, Services alta rápida | Client; uploads; Audit; Service | 03 F05; R15/R18 | U02/U03/U05 |
| F06/F07 | Órdenes y estados | Verificado estático | services, Service, schemas, Services y ServiceDetail | Client/Equipment/User/ServiceItem; Audit | 03 F06/F07; H12/H21; diagramas orden/estados | U02/U03 |
| F08 | Productos e inventario | Verificado estático | products, inventory, service_item, Inventory y Products | Service; stock/locks; Audit; helper desconectado | 03 F08; R22–R27; H08/H09 | U02/U04 |
| F09 | Pagos | Verificado estático | payments, model/schema payment, Payments | Service.items/pagos; Client; Audit | 03 F09; H07/H14/H21; diagrama pagos | U02/U04 |
| F10/F11 | Comprobantes y PDF | Verificado estático | invoices, model/schema invoice, Invoices, ServiceDetail | Service/Client; Decimal; Audit; ReportLab; Blob | 03 F10/F11; H01/H07/H11; diagrama comprobantes | U02/U03/U04 |
| F12 | Licencias | Verificado estático | licenses, model/schema license, Licenses | Client/Equipment; Audit; clipboard; date.today | 03 F12; H03/H15; diagrama licencias | U02/U03 |
| F13 | Carga y captura QR | Verificado estático | uploads, ImageUploadControl, MobileCameraUpload, main/static | Memoria; disco; qrserver; HTTP polling | 03 F13; H05/H16; diagrama captura | U03/U05/U09 |
| F14 | Dashboard | Verificado estático | dashboard, schema y Dashboard activo | Client/Service/Product/Payment | 03 F14; H14; contratos | U02/U03 |
| F15 | Auditoría y notificación | Verificado estático | audit/notifications routes/models/schemas/services, Audit, Services | User/Client/Service; sesión compartida | 03 F15; H10/H11/H18 | U02; sin entrega externa implementada |
| F16 | Navegación y componentes | Verificado estático | App, main, Layout, Sidebar, Navbar, Modal, ProtectedRoute, CSS/HTML | AuthContext; permissions; Router; páginas | 01/02; 03 F16; H08/H09/H18 | U03 |
| F17 | Inicialización, configuración y despliegue | Verificado estático | db, core/config, Dockerfiles, Compose, SQL, Alembic | Todos los modelos; PostgreSQL; npm/pip; filesystem | 09 completo; H25–H28; diagrama arranque | U01/U02/U06 |
| F17-T | Pruebas | Verificado estático | backend/tests/test_main.py y scripts package | TestClient; auth; Settings; DB no aislada | 03 F17; H29; verificacion.md | U03; no ejecución por límites de alcance |
| X01 | Documentación y dependencias declaradas | Verificado estático | README, openapi, requirements, package/lock, gitignore | Contraste implementación; imports; manifest | 08; contraste-openapi.json; H17/H30 | U03/U08; sin lectura de terceros instalados |

Los grupos anteriores se expanden archivo por archivo abajo. `inventario.json` añade imports y símbolos con línea para rastreo mecánico. Fichas F01–F17 del catálogo describen entradas, actores, secuencias, salidas, errores y persistencia; cada suboperación HTTP figura en 06. Las referencias a Hxx se resuelven en 10.

## Cobertura archivo por archivo

| Archivo | Líneas / bytes binarios | Módulo | Estado | Evidencia y dependencia inspeccionada |
|---|---|---|---|---|
| [.gitignore](../../.gitignore) | 26 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [README.md](../../README.md) | 49 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [docker-compose.yml](../../docker-compose.yml) | 60 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [openapi.json](../../openapi.json) | 1 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/Dockerfile](../../backend/Dockerfile) | 21 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic.ini](../../backend/alembic.ini) | 37 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/requirements.txt](../../backend/requirements.txt) | 15 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/env.py](../../backend/alembic/env.py) | 104 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/script.py.mako](../../backend/alembic/script.py.mako) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/alembic/versions/0001_initial_schema.py](../../backend/alembic/versions/0001_initial_schema.py) | 22 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/versions/0002_service_items.py](../../backend/alembic/versions/0002_service_items.py) | 106 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/versions/0003_equipo_opcional_servicios.py](../../backend/alembic/versions/0003_equipo_opcional_servicios.py) | 25 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/versions/0004_estado_pagos.py](../../backend/alembic/versions/0004_estado_pagos.py) | 62 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/alembic/versions/c3a1528905ae_crear_comprobantes_de_facturacion.py](../../backend/alembic/versions/c3a1528905ae_crear_comprobantes_de_facturacion.py) | 402 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/__init__.py](../../backend/app/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/main.py](../../backend/app/main.py) | 54 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/__init__.py](../../backend/app/api/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/api/deps.py](../../backend/app/api/deps.py) | 74 | F01/F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/__init__.py](../../backend/app/api/routes/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/api/routes/audit.py](../../backend/app/api/routes/audit.py) | 20 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/auth.py](../../backend/app/api/routes/auth.py) | 56 | F01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/clients.py](../../backend/app/api/routes/clients.py) | 82 | F04 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/companies.py](../../backend/app/api/routes/companies.py) | 199 | F02 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/dashboard.py](../../backend/app/api/routes/dashboard.py) | 54 | F14 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/equipment.py](../../backend/app/api/routes/equipment.py) | 57 | F05 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/inventory.py](../../backend/app/api/routes/inventory.py) | 0 | F08 | verificado (estático) | Vacío confirmado |
| [backend/app/api/routes/invoices.py](../../backend/app/api/routes/invoices.py) | 1494 | F10/F11 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/licenses.py](../../backend/app/api/routes/licenses.py) | 207 | F12 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/notifications.py](../../backend/app/api/routes/notifications.py) | 34 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/payments.py](../../backend/app/api/routes/payments.py) | 236 | F09 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/products.py](../../backend/app/api/routes/products.py) | 51 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/services.py](../../backend/app/api/routes/services.py) | 272 | F06/F07/F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/uploads.py](../../backend/app/api/routes/uploads.py) | 118 | F13 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/api/routes/users.py](../../backend/app/api/routes/users.py) | 137 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/core/__init__.py](../../backend/app/core/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/core/config.py](../../backend/app/core/config.py) | 22 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/core/rbac.py](../../backend/app/core/rbac.py) | 21 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/core/security.py](../../backend/app/core/security.py) | 33 | F01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/db/__init__.py](../../backend/app/db/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/db/base.py](../../backend/app/db/base.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/db/init_db.py](../../backend/app/db/init_db.py) | 174 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/db/session.py](../../backend/app/db/session.py) | 24 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/__init__.py](../../backend/app/models/__init__.py) | 36 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/audit.py](../../backend/app/models/audit.py) | 22 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/client.py](../../backend/app/models/client.py) | 27 | F04 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/company.py](../../backend/app/models/company.py) | 22 | F02 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/equipment.py](../../backend/app/models/equipment.py) | 25 | F05 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/inventory.py](../../backend/app/models/inventory.py) | 29 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/invoice.py](../../backend/app/models/invoice.py) | 69 | F10/F11 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/license.py](../../backend/app/models/license.py) | 34 | F12 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/notification.py](../../backend/app/models/notification.py) | 23 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/payment.py](../../backend/app/models/payment.py) | 36 | F09 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/product.py](../../backend/app/models/product.py) | 26 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/role.py](../../backend/app/models/role.py) | 11 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/service.py](../../backend/app/models/service.py) | 56 | F06/F07 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/service_item.py](../../backend/app/models/service_item.py) | 58 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/models/user.py](../../backend/app/models/user.py) | 25 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/__init__.py](../../backend/app/schemas/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/schemas/audit.py](../../backend/app/schemas/audit.py) | 13 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/auth.py](../../backend/app/schemas/auth.py) | 17 | F01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/client.py](../../backend/app/schemas/client.py) | 29 | F04 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/company.py](../../backend/app/schemas/company.py) | 48 | F02 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/dashboard.py](../../backend/app/schemas/dashboard.py) | 9 | F14 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/equipment.py](../../backend/app/schemas/equipment.py) | 20 | F05 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/inventory.py](../../backend/app/schemas/inventory.py) | 21 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/invoice.py](../../backend/app/schemas/invoice.py) | 72 | F10/F11 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/license.py](../../backend/app/schemas/license.py) | 57 | F12 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/notification.py](../../backend/app/schemas/notification.py) | 16 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/payment.py](../../backend/app/schemas/payment.py) | 38 | F09 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/product.py](../../backend/app/schemas/product.py) | 31 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/service.py](../../backend/app/schemas/service.py) | 49 | F06/F07 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/service_item.py](../../backend/app/schemas/service_item.py) | 19 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/schemas/user.py](../../backend/app/schemas/user.py) | 34 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/services/__init__.py](../../backend/app/services/__init__.py) | 0 | F17 | verificado (estático) | Vacío confirmado |
| [backend/app/services/audit_service.py](../../backend/app/services/audit_service.py) | 23 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/services/inventory_service.py](../../backend/app/services/inventory_service.py) | 49 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/app/services/notification_service.py](../../backend/app/services/notification_service.py) | 26 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [backend/static/uploads/95431c21f4df499bbd689e8789694e93.jpg](../../backend/static/uploads/95431c21f4df499bbd689e8789694e93.jpg) | 111155 bytes | F17 | documentado (inventario, contenido excluido) | Contenido excluido; metadata únicamente |
| [backend/static/uploads/qr_3975c2a899954ad29f076818703f00d1_1a63c7e7.jpg](../../backend/static/uploads/qr_3975c2a899954ad29f076818703f00d1_1a63c7e7.jpg) | 15 bytes | F17 | documentado (inventario, contenido excluido) | Contenido excluido; metadata únicamente |
| [backend/tests/test_main.py](../../backend/tests/test_main.py) | 22 | F17-T | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [database/init.sql](../../database/init.sql) | 2 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/Dockerfile](../../frontend/Dockerfile) | 12 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/index.html](../../frontend/index.html) | 12 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/package-lock.json](../../frontend/package-lock.json) | 2967 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/package.json](../../frontend/package.json) | 25 | X01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/postcss.config.cjs](../../frontend/postcss.config.cjs) | 6 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/tailwind.config.cjs](../../frontend/tailwind.config.cjs) | 20 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/vite.config.js](../../frontend/vite.config.js) | 13 | F17 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/App.jsx](../../frontend/src/App.jsx) | 349 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/index.css](../../frontend/src/index.css) | 71 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/main.jsx](../../frontend/src/main.jsx) | 10 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/components/ImageUploadControl.jsx](../../frontend/src/components/ImageUploadControl.jsx) | 276 | F13 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/components/Layout.jsx](../../frontend/src/components/Layout.jsx) | 32 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/components/Modal.jsx](../../frontend/src/components/Modal.jsx) | 0 | F16 | verificado (estático) | Vacío confirmado |
| [frontend/src/components/Navbar.jsx](../../frontend/src/components/Navbar.jsx) | 84 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/components/ProtectedRoute.jsx](../../frontend/src/components/ProtectedRoute.jsx) | 262 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/components/Sidebar.jsx](../../frontend/src/components/Sidebar.jsx) | 459 | F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/context/AuthContext.jsx](../../frontend/src/context/AuthContext.jsx) | 96 | F01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Audit.jsx](../../frontend/src/pages/Audit.jsx) | 394 | F15 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Clients.jsx](../../frontend/src/pages/Clients.jsx) | 991 | F04 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Dashboard.jsx](../../frontend/src/pages/Dashboard.jsx) | 142 | F14 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Equipment.jsx](../../frontend/src/pages/Equipment.jsx) | 972 | F05 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Inventory.jsx](../../frontend/src/pages/Inventory.jsx) | 897 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Invoices.jsx](../../frontend/src/pages/Invoices.jsx) | 750 | F10/F11 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Licenses.jsx](../../frontend/src/pages/Licenses.jsx) | 730 | F12 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Login.jsx](../../frontend/src/pages/Login.jsx) | 434 | F01 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/MobileCameraUpload.jsx](../../frontend/src/pages/MobileCameraUpload.jsx) | 194 | F13 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Payments.jsx](../../frontend/src/pages/Payments.jsx) | 1512 | F09 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Products.jsx](../../frontend/src/pages/Products.jsx) | 1014 | F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/ServiceDetail.jsx](../../frontend/src/pages/ServiceDetail.jsx) | 1907 | F06/F07/F08/F10 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Services.jsx](../../frontend/src/pages/Services.jsx) | 1290 | F06/F07/F08 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Superadmin.jsx](../../frontend/src/pages/Superadmin.jsx) | 409 | F02 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/pages/Users.jsx](../../frontend/src/pages/Users.jsx) | 574 | F03 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/services/api.js](../../frontend/src/services/api.js) | 27 | F01/F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |
| [frontend/src/utils/permissions.js](../../frontend/src/utils/permissions.js) | 73 | F03/F16 | verificado (estático) | Declaraciones y recorrido; hash/imports/símbolos en inventario.json |

## Reanudar o actualizar el análisis

Si cambia el código, comparar SHA-256 contra inventario.json, reabrir como en análisis los archivos cambiados y sus llamadores, revisar las fichas/diagramas correspondientes y contrastar de nuevo esquemas y rutas. No usar el openapi.json histórico como autoridad. No marcar una prueba de runtime aprobada a partir de esta revisión estática.

Puntos que requieren información nueva: U01–U10 en [hallazgos](10-hallazgos-incertidumbres.md). No hay módulo propio conocido pendiente de primera inspección. Las exclusiones se mantienen expresas. Resultado de controles finales en [verificación](verificacion.md).
