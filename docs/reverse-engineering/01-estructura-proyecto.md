# Estructura del proyecto

## Mapa del código propio

```text
/
├── README.md                       Declaraciones y arranque anunciado
├── openapi.json                    Exportación histórica, no contrato vigente
├── docker-compose.yml              PostgreSQL, API y Vite
├── database/init.sql               Extensión uuid-ossp
├── backend/
│   ├── Dockerfile, requirements.txt, alembic.ini
│   ├── alembic/env.py, script.py.mako, versions/ (5 revisiones)
│   ├── app/
│   │   ├── main.py                  Aplicación, CORS, static y routers
│   │   ├── api/deps.py              Usuario actual, roles y permisos
│   │   ├── api/routes/              Módulos HTTP; inventory.py vacío
│   │   ├── core/                    Configuración, JWT, bcrypt, RBAC antiguo
│   │   ├── db/                      Motor, sesiones e inicialización
│   │   ├── models/                  15 tablas ORM en 14 módulos de entidad
│   │   ├── schemas/                 Contratos Pydantic
│   │   └── services/                Auditoría, notificaciones e inventario auxiliar
│   ├── tests/test_main.py           Dos pruebas de login
│   └── static/uploads/             Dos JPG inventariados sin abrir
└── frontend/
    ├── Dockerfile, package.json, package-lock.json
    ├── index.html, vite.config.js, tailwind.config.cjs, postcss.config.cjs
    └── src/
        ├── main.jsx, App.jsx, index.css
        ├── context/AuthContext.jsx
        ├── services/api.js
        ├── utils/permissions.js
        ├── components/             Navegación, captura; Modal.jsx vacío
        └── pages/                  Pantallas de negocio y dos variantes de catálogo
```

Este mapa se deriva del inventario recursivo de archivos propios. La lista exacta, incluidos archivos vacíos e inicializadores, figura en [trazabilidad](trazabilidad.md) y `inventario.json`. Se excluyeron carpetas de dependencias, cachés, metadatos y artefactos compilados. `src/components` se analizó porque es código propio, distinto de las dependencias como `node_modules`.

## Entradas y composición

| Entrada | Recorrido | Evidencia |
|---|---|---|
| Navegador | `index.html` → `main.jsx` → `App` → AuthProvider/BrowserRouter → Layout/Outlet → pantalla | `frontend/index.html:9-10`; `frontend/src/main.jsx:6-10`; `frontend/src/App.jsx:85-348` |
| API | Uvicorn carga `app.main:app`; FastAPI registra 14 routers | `backend/Dockerfile:21`; `backend/app/main.py:26-54` |
| Inicialización | `python -m app.db.init_db` crea tablas y datos de demostración | `backend/app/db/init_db.py:9-174` |
| Migración | Alembic lee su INI y metadatos; upgrade/downgrade en versions | `backend/alembic/env.py:25-104` |
| Persistencia | motor y `SessionLocal`; `get_db` entrega una sesión por petición | `backend/app/db/session.py:5-24` |
| Captura móvil | Ruta pública `/captura-movil/:sessionId` → multipart de uploads | `frontend/src/App.jsx:98-101`; `frontend/src/pages/MobileCameraUpload.jsx:35-58` |

## Responsabilidades por carpeta

Los routers contienen tanto HTTP como validaciones y transacciones. `models` define almacenamiento y relaciones; `schemas` define cuerpos y respuestas. `services` no constituye una capa obligatoria: los routers acceden directamente al ORM. En el cliente, cada página administra su estado, carga datos y transforma respuestas; Axios centraliza token y tratamiento de 401. Evidencias: `backend/app/api/routes/services.py:60-272`, `backend/app/services/audit_service.py:5-23`, `frontend/src/pages/Payments.jsx:147-543`, `frontend/src/services/api.js:3-25`.

## Archivos desconectados o incompletos

`backend/app/api/routes/inventory.py`, `backend/app/db/base.py`, `backend/alembic/script.py.mako` y `frontend/src/components/Modal.jsx` están vacíos. `core/rbac.py` y `services/inventory_service.py` tienen implementaciones sin referencias desde los recorridos registrados. `pages/Products.jsx` no está importado por App, que usa `Inventory`. `components/ProtectedRoute.jsx` exporta una variante de Dashboard y no se usa: el guard efectivo está dentro de App. Ver evidencias y límites de esta búsqueda en H08 y H09 de [hallazgos](10-hallazgos-incertidumbres.md).
