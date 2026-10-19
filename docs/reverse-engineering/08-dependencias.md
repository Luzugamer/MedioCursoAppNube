# Dependencias internas y externas

## Alcance de verificación

Versiones declaradas y resueltas se leen exclusivamente de manifiestos del proyecto. **No se leyeron ni ejecutaron dependencias instaladas.** No se consultaron registros externos ni se hizo auditoría de vulnerabilidades; no se afirma que el entorno instalado coincida con estos archivos.

## Backend

Fuente: `backend/requirements.txt:1-15` y imports de `backend/app`. Python base 3.12-slim declarado en `backend/Dockerfile:1`; PostgreSQL 16-alpine en `docker-compose.yml:4`.

| Dependencia fijada | Uso comprobado o previsto por configuración |
|---|---|
| `fastapi==0.110.0` | API, rutas, dependencias, validación HTTP |
| `uvicorn[standard]==0.28.0` | Proceso ASGI en CMD del contenedor |
| `sqlalchemy==2.0.28` | ORM, SQL, motor, pool y sesiones |
| `alembic==1.13.1` | Migraciones y stamp de arranque |
| `psycopg2-binary==2.9.9` | Driver PostgreSQL de DATABASE_URL |
| `pydantic==2.6.4` | Schemas de solicitud/respuesta |
| `pydantic-settings==2.2.1` | Settings desde entorno y env_file |
| `email-validator==2.1.1` | Soporte declarado para EmailStr de schemas |
| `python-jose[cryptography]==3.3.0` | JWT encode/decode mediante jose |
| `passlib[bcrypt]==1.7.4` | CryptContext para bcrypt |
| `bcrypt==4.0.1` | Backend de hashing fijado |
| `python-multipart==0.0.9` | Procesamiento de multipart File/UploadFile |
| `pytest==8.1.1` | Suite declarada; dos tests de login |
| `httpx==0.27.0` | Dependencia declarada de pruebas TestClient; no cliente externo de negocio |
| `reportlab==4.2.2` | Generación PDF de comprobantes |

No hay lockfile Python de dependencias transitivas en el inventario. Los extras `[standard]`, `[cryptography]` y `[bcrypt]` amplían resolución, pero sus versiones transitivas instaladas son desconocidas. Los imports de biblioteca estándar relevantes incluyen datetime, decimal, uuid, os, pathlib, io y xml.sax.saxutils; se usan para fechas, dinero, identificadores, disco, buffers PDF y escape de texto. Fuentes: imports de `backend/app/api/routes/invoices.py:1-4`, `uploads.py:1-4`, `payments.py:1-2`, `core/security.py:1-2`.

## Frontend

Fuente: `frontend/package.json:11-23`; resoluciones en `frontend/package-lock.json`, formato lockfileVersion 3. Las claves node_modules siguientes son metadatos del JSON, no carpetas inspeccionadas. Node 20-alpine en `frontend/Dockerfile:1`.

| Paquete | Rango declarado | Resolución lock | Ámbito | Responsabilidad |
|---|---|---|---|---|
| `axios` | `^1.6.8` | `1.20.0` | dependencies | Cliente HTTP e interceptores |
| `lucide-react` | `^0.359.0` | `0.359.0` | dependencies | Iconos JSX |
| `react` | `^18.2.0` | `18.3.1` | dependencies | Componentes, hooks y contexto |
| `react-dom` | `^18.2.0` | `18.3.1` | dependencies | Montaje DOM |
| `react-router-dom` | `^6.22.3` | `6.30.6` | dependencies | BrowserRouter, rutas, parametros y navegacion |
| `@vitejs/plugin-react` | `^4.2.1` | `4.7.0` | devDependencies | Transformacion JSX e integracion React/Vite |
| `autoprefixer` | `^10.4.19` | `10.6.1` | devDependencies | Postprocesado CSS |
| `postcss` | `^8.4.38` | `8.5.28` | devDependencies | Pipeline CSS |
| `tailwindcss` | `^3.4.1` | `3.4.19` | devDependencies | Clases de utilidad CSS |
| `vite` | `^5.1.6` | `5.4.21` | devDependencies | Servidor desarrollo y build |

`npm install` se usa en Dockerfile (no npm ci). Scripts: dev=vite, build=vite build, preview=vite preview. No script test/lint declarado. Fuentes: `frontend/Dockerfile:5-12`, `frontend/package.json:6-9`.

## Dependencias internas

[Diagrama de dependencias](diagramas/dependencias.mmd). Las relaciones se obtienen de imports, composición React y llamadas de routers. No se encontró capa Repository independiente ni bus de eventos.

| Módulo consumidor | Proveedores principales | Evidencia |
|---|---|---|
| main | 14 routers, settings, StaticFiles y CORS | `backend/app/main.py:1-54` |
| deps | session, User, jose, settings | `backend/app/api/deps.py:1-74` |
| routers de negocio | models, schemas, deps y audit_service | `backend/app/api/routes/services.py:1-21` y firmas en 06 |
| notificaciones | NotificationService → Notification y log_audit | `backend/app/api/routes/notifications.py:26-33`; `backend/app/services/notification_service.py:1-26` |
| init_db | modelos registrados por paquete __init__, session y hash | `backend/app/db/init_db.py:1-10`; `backend/app/models/__init__.py:1-14` |
| App | AuthProvider, Layout, permisos y páginas | `frontend/src/App.jsx:11-33` |
| Formularios | api.js, hooks y helpers/componentes locales | `frontend/src/pages/Services.jsx:1-24`; `frontend/src/pages/Users.jsx:1-24` |
| Upload UI | api.js, FileReader, captura HTML y QR externo | `frontend/src/components/ImageUploadControl.jsx:26-106`; `frontend/src/pages/MobileCameraUpload.jsx:16-58` |

## Integraciones y herramientas de despliegue

Docker Compose conecta tres servicios; backend instala gcc, libpq-dev y curl en imagen. No se encontró CI, proxy reverse, terminación TLS, gestor de colas, Redis ni almacenamiento cloud en el inventario. Hay recursos de imagen externos y QR descritos en [06](06-apis-integraciones.md). Esta ausencia se limita a la copia local, no a infraestructura ajena. Fuentes: ambos Dockerfile, docker-compose.yml e inventario completo.

## Inventario completo del lock frontend

El lock contiene 202 entradas de paquetes, además de la raíz. Se listan todas sus versiones y banderas; no todas son instalables en el mismo sistema operativo. `optional` y `dev` reproducen el manifiesto.

| Ruta en lock | Versión | dev | optional |
|---|---|---|---|
| `node_modules/@alloc/quick-lru` | `5.3.0` | True | False |
| `node_modules/@babel/code-frame` | `7.29.7` | True | False |
| `node_modules/@babel/compat-data` | `7.29.7` | True | False |
| `node_modules/@babel/core` | `7.29.7` | True | False |
| `node_modules/@babel/generator` | `7.29.8` | True | False |
| `node_modules/@babel/helper-compilation-targets` | `7.29.7` | True | False |
| `node_modules/@babel/helper-globals` | `7.29.7` | True | False |
| `node_modules/@babel/helper-module-imports` | `7.29.7` | True | False |
| `node_modules/@babel/helper-module-transforms` | `7.29.7` | True | False |
| `node_modules/@babel/helper-plugin-utils` | `7.29.7` | True | False |
| `node_modules/@babel/helper-string-parser` | `7.29.7` | True | False |
| `node_modules/@babel/helper-validator-identifier` | `7.29.7` | True | False |
| `node_modules/@babel/helper-validator-option` | `7.29.7` | True | False |
| `node_modules/@babel/helpers` | `7.29.7` | True | False |
| `node_modules/@babel/parser` | `7.29.9` | True | False |
| `node_modules/@babel/plugin-transform-react-jsx-self` | `7.29.7` | True | False |
| `node_modules/@babel/plugin-transform-react-jsx-source` | `7.29.7` | True | False |
| `node_modules/@babel/template` | `7.29.7` | True | False |
| `node_modules/@babel/traverse` | `7.29.8` | True | False |
| `node_modules/@babel/types` | `7.29.8` | True | False |
| `node_modules/@esbuild/aix-ppc64` | `0.21.5` | True | True |
| `node_modules/@esbuild/android-arm` | `0.21.5` | True | True |
| `node_modules/@esbuild/android-arm64` | `0.21.5` | True | True |
| `node_modules/@esbuild/android-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/darwin-arm64` | `0.21.5` | True | True |
| `node_modules/@esbuild/darwin-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/freebsd-arm64` | `0.21.5` | True | True |
| `node_modules/@esbuild/freebsd-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-arm` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-arm64` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-ia32` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-loong64` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-mips64el` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-ppc64` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-riscv64` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-s390x` | `0.21.5` | True | True |
| `node_modules/@esbuild/linux-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/netbsd-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/openbsd-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/sunos-x64` | `0.21.5` | True | True |
| `node_modules/@esbuild/win32-arm64` | `0.21.5` | True | True |
| `node_modules/@esbuild/win32-ia32` | `0.21.5` | True | True |
| `node_modules/@esbuild/win32-x64` | `0.21.5` | True | True |
| `node_modules/@jridgewell/gen-mapping` | `0.3.13` | True | False |
| `node_modules/@jridgewell/remapping` | `2.3.5` | True | False |
| `node_modules/@jridgewell/resolve-uri` | `3.1.2` | True | False |
| `node_modules/@jridgewell/sourcemap-codec` | `1.6.0` | True | False |
| `node_modules/@jridgewell/trace-mapping` | `0.3.31` | True | False |
| `node_modules/@napi-rs/lzma-linux-x64-gnu` | `1.5.1` | True | True |
| `node_modules/@nodelib/fs.scandir` | `2.1.5` | True | False |
| `node_modules/@nodelib/fs.stat` | `2.0.5` | True | False |
| `node_modules/@nodelib/fs.walk` | `1.2.8` | True | False |
| `node_modules/@remix-run/router` | `1.23.4` | False | False |
| `node_modules/@rolldown/pluginutils` | `1.0.0-beta.27` | True | False |
| `node_modules/@rollup/rollup-android-arm-eabi` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-android-arm64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-darwin-arm64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-darwin-x64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-freebsd-arm64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-freebsd-x64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-arm-gnueabihf` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-arm-musleabihf` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-arm64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-arm64-musl` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-loong64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-loong64-musl` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-ppc64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-ppc64-musl` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-riscv64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-riscv64-musl` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-s390x-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-x64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-linux-x64-musl` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-openbsd-x64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-openharmony-arm64` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-win32-arm64-msvc` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-win32-ia32-msvc` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-win32-x64-gnu` | `4.63.4` | True | True |
| `node_modules/@rollup/rollup-win32-x64-msvc` | `4.63.4` | True | True |
| `node_modules/@types/babel__core` | `7.20.5` | True | False |
| `node_modules/@types/babel__generator` | `7.27.0` | True | False |
| `node_modules/@types/babel__template` | `7.4.4` | True | False |
| `node_modules/@types/babel__traverse` | `7.28.0` | True | False |
| `node_modules/@types/estree` | `1.0.9` | True | False |
| `node_modules/@vitejs/plugin-react` | `4.7.0` | True | False |
| `node_modules/agent-base` | `6.0.2` | False | False |
| `node_modules/any-promise` | `1.3.0` | True | False |
| `node_modules/anymatch` | `3.1.3` | True | False |
| `node_modules/arg` | `5.0.2` | True | False |
| `node_modules/asynckit` | `0.4.0` | False | False |
| `node_modules/autoprefixer` | `10.6.1` | True | False |
| `node_modules/axios` | `1.20.0` | False | False |
| `node_modules/baseline-browser-mapping` | `2.11.25` | True | False |
| `node_modules/binary-extensions` | `2.3.0` | True | False |
| `node_modules/braces` | `3.0.3` | True | False |
| `node_modules/browserslist` | `4.29.0` | True | False |
| `node_modules/call-bind-apply-helpers` | `1.0.2` | False | False |
| `node_modules/camelcase-css` | `2.0.1` | True | False |
| `node_modules/caniuse-lite` | `1.0.30001810` | True | False |
| `node_modules/chokidar` | `3.6.0` | True | False |
| `node_modules/chokidar/node_modules/glob-parent` | `5.1.2` | True | False |
| `node_modules/combined-stream` | `1.0.8` | False | False |
| `node_modules/commander` | `4.1.1` | True | False |
| `node_modules/convert-source-map` | `2.0.0` | True | False |
| `node_modules/cssesc` | `3.0.0` | True | False |
| `node_modules/debug` | `4.4.3` | False | False |
| `node_modules/delayed-stream` | `1.0.0` | False | False |
| `node_modules/didyoumean` | `1.2.2` | True | False |
| `node_modules/dlv` | `1.1.3` | True | False |
| `node_modules/dunder-proto` | `1.0.1` | False | False |
| `node_modules/electron-to-chromium` | `1.5.437` | True | False |
| `node_modules/es-define-property` | `1.0.1` | False | False |
| `node_modules/es-errors` | `1.3.0` | False | False |
| `node_modules/es-object-atoms` | `1.1.2` | False | False |
| `node_modules/es-set-tostringtag` | `2.1.0` | False | False |
| `node_modules/esbuild` | `0.21.5` | True | False |
| `node_modules/escalade` | `3.2.0` | True | False |
| `node_modules/fast-glob` | `3.3.3` | True | False |
| `node_modules/fast-glob/node_modules/glob-parent` | `5.1.2` | True | False |
| `node_modules/fastq` | `1.20.3` | True | False |
| `node_modules/fill-range` | `7.1.1` | True | False |
| `node_modules/follow-redirects` | `1.16.0` | False | False |
| `node_modules/form-data` | `4.0.6` | False | False |
| `node_modules/fraction.js` | `5.3.4` | True | False |
| `node_modules/fsevents` | `2.3.3` | True | True |
| `node_modules/function-bind` | `1.1.2` | False | False |
| `node_modules/gensync` | `1.0.0-beta.2` | True | False |
| `node_modules/get-intrinsic` | `1.3.0` | False | False |
| `node_modules/get-proto` | `1.0.1` | False | False |
| `node_modules/glob-parent` | `6.0.2` | True | False |
| `node_modules/gopd` | `1.2.0` | False | False |
| `node_modules/has-symbols` | `1.1.0` | False | False |
| `node_modules/has-tostringtag` | `1.0.2` | False | False |
| `node_modules/hasown` | `2.0.4` | False | False |
| `node_modules/https-proxy-agent` | `5.0.1` | False | False |
| `node_modules/is-binary-path` | `2.1.0` | True | False |
| `node_modules/is-core-module` | `2.17.0` | True | False |
| `node_modules/is-extglob` | `2.1.1` | True | False |
| `node_modules/is-glob` | `4.0.3` | True | False |
| `node_modules/is-number` | `7.0.0` | True | False |
| `node_modules/jiti` | `1.21.7` | True | False |
| `node_modules/js-tokens` | `4.0.0` | False | False |
| `node_modules/jsesc` | `3.1.0` | True | False |
| `node_modules/json5` | `2.2.3` | True | False |
| `node_modules/lilconfig` | `3.1.3` | True | False |
| `node_modules/lines-and-columns` | `1.2.4` | True | False |
| `node_modules/loose-envify` | `1.4.0` | False | False |
| `node_modules/lru-cache` | `5.1.1` | True | False |
| `node_modules/lucide-react` | `0.359.0` | False | False |
| `node_modules/math-intrinsics` | `1.1.0` | False | False |
| `node_modules/merge2` | `1.4.1` | True | False |
| `node_modules/micromatch` | `4.0.8` | True | False |
| `node_modules/mime-db` | `1.52.0` | False | False |
| `node_modules/mime-types` | `2.1.35` | False | False |
| `node_modules/ms` | `2.1.3` | False | False |
| `node_modules/mz` | `2.7.0` | True | False |
| `node_modules/nanoid` | `3.3.19` | True | False |
| `node_modules/node-releases` | `2.0.56` | True | False |
| `node_modules/normalize-path` | `3.0.0` | True | False |
| `node_modules/object-assign` | `4.1.1` | True | False |
| `node_modules/object-hash` | `3.0.0` | True | False |
| `node_modules/path-parse` | `1.0.7` | True | False |
| `node_modules/picocolors` | `1.1.1` | True | False |
| `node_modules/picomatch` | `2.3.2` | True | False |
| `node_modules/pirates` | `4.0.7` | True | False |
| `node_modules/postcss` | `8.5.28` | True | False |
| `node_modules/postcss-import` | `15.1.0` | True | False |
| `node_modules/postcss-js` | `4.1.0` | True | False |
| `node_modules/postcss-load-config` | `6.0.1` | True | False |
| `node_modules/postcss-nested` | `6.2.0` | True | False |
| `node_modules/postcss-selector-parser` | `6.1.4` | True | False |
| `node_modules/postcss-value-parser` | `4.2.0` | True | False |
| `node_modules/proxy-from-env` | `2.1.0` | False | False |
| `node_modules/queue-microtask` | `1.2.3` | True | False |
| `node_modules/react` | `18.3.1` | False | False |
| `node_modules/react-dom` | `18.3.1` | False | False |
| `node_modules/react-refresh` | `0.17.0` | True | False |
| `node_modules/react-router` | `6.30.6` | False | False |
| `node_modules/react-router-dom` | `6.30.6` | False | False |
| `node_modules/read-cache` | `1.0.2` | True | False |
| `node_modules/readdirp` | `3.6.0` | True | False |
| `node_modules/resolve` | `1.22.12` | True | False |
| `node_modules/reusify` | `1.1.0` | True | False |
| `node_modules/rollup` | `4.63.4` | True | False |
| `node_modules/run-parallel` | `1.2.0` | True | False |
| `node_modules/scheduler` | `0.23.2` | False | False |
| `node_modules/semver` | `6.3.1` | True | False |
| `node_modules/source-map-js` | `1.2.1` | True | False |
| `node_modules/sucrase` | `3.35.1` | True | False |
| `node_modules/supports-preserve-symlinks-flag` | `1.0.0` | True | False |
| `node_modules/tailwindcss` | `3.4.19` | True | False |
| `node_modules/thenify` | `3.3.1` | True | False |
| `node_modules/thenify-all` | `1.6.0` | True | False |
| `node_modules/tinyglobby` | `0.2.17` | True | False |
| `node_modules/tinyglobby/node_modules/fdir` | `6.5.0` | True | False |
| `node_modules/tinyglobby/node_modules/picomatch` | `4.0.7` | True | False |
| `node_modules/to-regex-range` | `5.0.1` | True | False |
| `node_modules/ts-interface-checker` | `0.1.13` | True | False |
| `node_modules/update-browserslist-db` | `1.3.3` | True | False |
| `node_modules/util-deprecate` | `1.0.2` | True | False |
| `node_modules/vite` | `5.4.21` | True | False |
| `node_modules/yallist` | `3.1.1` | True | False |
