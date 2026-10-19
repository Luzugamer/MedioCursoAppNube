# Configuración y despliegue reconstruidos

Este documento describe lo declarado por el proyecto. No se ejecutó Docker, npm, pytest, Alembic ni init_db; no se importó la aplicación. Ningún `.env*` se abrió. Por tanto, valores efectivos, servicios activos y esquema instalado son **desconocidos**.

## Configuración deducida del código

| Variable | Consumidor / default o significado | Evidencia |
|---|---|---|
| PROJECT_NAME | Settings; SisTec API | `backend/app/core/config.py:6` |
| API_V1_STR | Settings; `/api`, usado por routers/OpenAPI/tokenUrl | `backend/app/core/config.py:7`; `backend/app/main.py:28,41-54` |
| SECRET_KEY | Firma/verificación JWT; existe default literal en fuente y Compose | `backend/app/core/config.py:8`; `docker-compose.yml:33`; `backend/app/core/security.py:32` |
| ALGORITHM | HS256 por defecto; Compose lo fija | `backend/app/core/config.py:9`; `docker-compose.yml:34` |
| ACCESS_TOKEN_EXPIRE_MINUTES | 480 por defecto y en Compose | `backend/app/core/config.py:10`; `docker-compose.yml:35` |
| DATABASE_URL | URL PostgreSQL con host `postgres:5432`; Compose la construye con POSTGRES_* | `backend/app/core/config.py:11`; `docker-compose.yml:32` |
| CORS_ORIGINS | String separado por comas; trim y eliminación de vacíos; localhost/127.0.0.1 en 5173/5174/5175 | `backend/app/core/config.py:12-16`; `docker-compose.yml:36` |
| POSTGRES_DB | Compose, default `sistec_db` | `docker-compose.yml:8,32` |
| POSTGRES_USER | Compose, default `sistec_user` | `docker-compose.yml:9,32` |
| POSTGRES_PASSWORD | Compose, default literal en fuente; no se reproduce aquí | `docker-compose.yml:10,32` |
| VITE_API_URL | Axios; default `http://localhost:8000/api`; Compose mismo valor literal | `frontend/src/services/api.js:3-5`; `docker-compose.yml:50` |
| PYTHONDONTWRITEBYTECODE | Imagen backend: 1 | `backend/Dockerfile:5` |
| PYTHONUNBUFFERED | Imagen backend: 1 | `backend/Dockerfile:6` |

Settings es sensible a mayúsculas y declara `env_file = ".env"` (`backend/app/core/config.py:18-22`). Se inspeccionó esa declaración, no el archivo. No se deduce la configuración efectiva a partir de defaults. Las credenciales de semilla y defaults de secretos ya están en fuente; su presencia está documentada sin copiar sus valores al informe.

## Topología Compose

| Servicio | Construcción/imagen | Puerto host → contenedor | Persistencia/montajes | Dependencia |
|---|---|---|---|---|
| postgres | postgres:16-alpine | 5433 → 5432 | volumen postgres_data; database/init.sql | healthcheck pg_isready cada 5 s, timeout 5 s, 5 intentos |
| backend | backend/Dockerfile, python:3.12-slim | 8000 → 8000 | backend/app → /app/app; backend/static → /app/static | PostgreSQL service_healthy |
| frontend | frontend/Dockerfile, node:20-alpine | 5173 → 5173 | frontend → /app; volumen anónimo /app/node_modules | depends_on backend, sin healthcheck propio |

Fuente: `docker-compose.yml:2-60`. Todos declaran restart always. La API y PostgreSQL se comunican por puerto interno 5432; un cliente del host usaría 5433. `init.sql` solo crea extensión uuid-ossp; no crea tablas de negocio (`database/init.sql:1-2`). UUID de uploads se genera en Python, no mediante esa extensión (`backend/app/api/routes/uploads.py:2,36,57`).

## Secuencia de arranque real declarada

1. Construcción backend: instala gcc/libpq-dev/curl, instala requirements y copia directorio. Frontend instala package/package-lock con npm install y copia directorio. Ambos usan WORKDIR `/app` (`backend/Dockerfile:1-21`, `frontend/Dockerfile:1-12`).
2. Backend ejecuta `python -m app.db.init_db`. Importar un modelo carga el paquete `app.models`, cuyo `__init__` importa todas las entidades, incluidas Company, License e Invoice. `Base.metadata.create_all` utiliza esos metadatos (`backend/app/models/__init__.py:1-14`, `backend/app/db/init_db.py:1-10`).
3. Semilla comprueba roles por nombre y los crea; empresa Demo por ID 1; usuarios por email; producto por empresa+código; licencia por empresa+clave. Las fechas de licencia se calculan al crear respecto de date.today. Existen passwords literales de demostración; no se generan aleatoriamente (`backend/app/db/init_db.py:15-157`).
4. Se intentan reajustar secuencias con setval y se silencian excepciones. No hay rollback dentro de esos except; la recuperación efectiva ante error SQL no está garantizada (`backend/app/db/init_db.py:45-51,159-168`).
5. Se ejecuta `alembic stamp head`, **no `upgrade head`**. Si los comandos anteriores terminan correctamente, se inicia Uvicorn en 0.0.0.0:8000 (`backend/Dockerfile:21`).
6. Frontend ejecuta Vite dev en 0.0.0.0:5173. Vite activa watch.usePolling. No se sirve una compilación estática mediante Nginx (`frontend/Dockerfile:12`; `frontend/vite.config.js:4-12`).

[Diagrama de arranque](diagramas/arranque.mmd). La descripción no constituye confirmación de que el arranque actual finalice correctamente.

## Historial de migraciones y divergencias

| Archivo | Revisión → anterior | upgrade | downgrade / límite |
|---|---|---|---|
| 0001_initial_schema.py | 0001 → null | pass | pass; no crea esquema inicial |
| 0002_service_items.py | 0002 → 0001 | Crea service_items e índices | Borra tabla/índices; depende de services/products preexistentes |
| 0003_equipo_opcional_servicios.py | 0003_equipo_opcional → 0002 | Hace services.equipo_id nullable | Revierte NOT NULL; filas sin equipo podrían impedirlo |
| 0004_estado_pagos.py | 0004 → 0003_equipo_opcional | Enum paymentstatus, columna estado default PAGADO e índice | Borra índice/columna/tipo |
| c3a1528905ae_crear_comprobantes_de_facturacion.py | 0005 → 0004 | Enums y tablas invoices/invoice_items | Borra tablas y enums; nombre de archivo no coincide con revisión interna |

Evidencia: `backend/alembic/versions/0001_initial_schema.py:11-22`, `0002_service_items.py:12-106`, `0003_equipo_opcional_servicios.py:6-25`, `0004_estado_pagos.py:7-62`, `c3a1528905ae_crear_comprobantes_de_facturacion.py:8-402`.

La revisión 0005 no contiene `empresa_id` en invoices ni su índice único compuesto actual. No se encontraron migraciones para crear companies/licenses, permisos de usuario, empresa_id multiempresa en las demás tablas o imagen_url. El esquema actual proviene de los modelos y create_all para tablas ausentes. **Inferido:** marcar head no prueba que una base preexistente tenga columnas actuales; create_all no representa una migración explícita de columnas existentes. La cadena histórica tampoco basta como instalación desde base vacía: 0001 es pass y 0002 referencia tablas no creadas. No se ejecutó ninguna de las dos estrategias sobre datos reales.

`alembic/env.py:60-94` usa sqlalchemy.url del INI; no la reemplaza por settings.DATABASE_URL. Por ello un cambio de credenciales/base por Compose podría dejar Alembic apuntando a otro destino o hacer fallar stamp. `script.py.mako` está vacío; no se verificó creación de nuevas revisiones. Estos son límites de reproducibilidad, no instrucciones para modificar el despliegue.

## Comandos existentes documentados, no ejecutados

El README indica desde la raíz:

```sh
docker compose up -d --build
docker compose down
```

`README.md:27-47` anuncia frontend localhost:5173, backend localhost:8000/docs y PostgreSQL localhost:5433. La copia analizada no posee metadatos Git utilizables (`git status` respondió que no es un repositorio); no se pudo asociar un commit a este estado. Las huellas SHA-256 sirven para identificar los archivos inspeccionados.

Los entrypoints locales equivalentes se deducen de Dockerfile, pero ejecutarlos fuera de contenedores requiere resolver PostgreSQL, URL de conexión y directorio de trabajo. `static/uploads` se construye desde cwd; ejecutar desde otro directorio cambia almacenamiento. No se ofrece como receta probada una instalación local adicional. Fuentes: `backend/app/api/routes/uploads.py:11-12`, `backend/app/main.py:23-31`, ambos Dockerfile.

## Condiciones operativas verificables y desconocidas

- Captura móvil requiere que el móvil resuelva origen de UI y API. Un QR formado con localhost apunta al propio dispositivo; Compose fija API a localhost. No se encontró proxy para `/static`, aunque las URLs de archivos son relativas. Evidencias: `frontend/src/components/ImageUploadControl.jsx:63-66,142`; `frontend/src/services/api.js:4`; `frontend/vite.config.js:4-13`.
- Las sesiones QR son memoria de proceso; reinicio o varios workers afectarían su visibilidad. Los archivos sí están en bind mount. No se implementan TTL o recolección de archivos. Evidencia: `backend/app/api/routes/uploads.py:16-118`; `docker-compose.yml:41`.
- La imagen hace COPY de directorios completos y no se encontró `.dockerignore` en el inventario. No se conoce qué archivos excluidos del análisis existirían al construir una imagen; no se inspeccionaron `.env*` para comprobarlo. Fuente: ambos Dockerfile e inventario.
- No se verificó TLS, DNS, backups, capacidad, monitoreo, proceso de restauración ni despliegue externo. El único diseño operativo visible es Compose. No se atribuye al proyecto infraestructura que no figura en archivos.
- Pruebas existentes usan `admin@siges.local`; semilla crea `admin@sistec.com`. No tienen overrides/fixtures de DB; éxito de login genera auditoría. Se inspeccionaron sin ejecutar. Evidencia: `backend/tests/test_main.py:1-22`, `backend/app/db/init_db.py:66-77`, `backend/app/api/routes/auth.py:32-40`.
