# Hallazgos, diferencias e incertidumbres

Estos hallazgos proceden de lectura y contraste del código. No se intentó explotar fallos, realizar peticiones ni modificar datos. «Confirmado» identifica una propiedad del código; «inferido» identifica su posible consecuencia operativa bajo las condiciones descritas. La prioridad orienta la lectura, no es una medición formal de severidad.

## Control de acceso y aislamiento

### H01 — PDF sin filtro de empresa — prioridad alta

**Confirmado:** `generate_invoice_pdf` exige `comprobantes.ver`, pero su consulta filtra solo Invoice.id. El GET JSON y la anulación sí filtran empresa. **Inferido:** un usuario con permiso puede obtener por ID un PDF de otra empresa si ese ID existe y no hay protección externa adicional. No se probó sobre datos. Evidencia: `backend/app/api/routes/invoices.py:351-371` frente a `118-127,301-310`.

### H02 — Asignación de rol global sin restringir rol destino — alta

**Confirmado:** `require_admin` permite ADMIN y SUPERADMIN; create_user toma rol_id del cuerpo y update_user asigna cualquier rol_id enviado. El endpoint de listado de roles oculta SUPERADMIN a ADMIN, pero no limita mutaciones. **Inferido:** un administrador empresarial podría asignarse o asignar a otro usuario un rol SUPERADMIN existente, obteniendo permisos globales en siguientes peticiones. Evidencia: `backend/app/api/deps.py:49-55`, `backend/app/api/routes/users.py:21-22,75-82,107-124`, `backend/app/api/deps.py:26-39`.

### H03 — Relaciones de licencia actualizables fuera del ámbito — alta

**Confirmado:** PUT valida empresa de la License, no de cliente_id/equipo_id nuevos; después carga esas relaciones y devuelve nombres. Alta valida empresa de ambos individualmente, pero tampoco su correspondencia mutua. **Inferido:** IDs existentes de otra empresa pueden crear relaciones cruzadas y exponer nombres/datos de equipo en respuesta de licencia. Evidencia: `backend/app/api/routes/licenses.py:90-103,144-180,33-39`; `backend/app/schemas/license.py:34-45`.

### H04 — Aislamiento distribuido con excepciones — alta

**Confirmado:** creaciones usan empresa del usuario o 1. SUPERADMIN consulta sin ámbito y puede crear equipo/servicio/comprobante de empresa 1 con referencias de otra empresa; consumo SUPERADMIN no exige misma empresa para producto y servicio. Responsable de Service tampoco se valida por empresa. Dashboard omite filtros para usuario sin empresa. **Inferido:** los registros pueden mezclar empresas aun con FK válidas. Evidencia: `backend/app/api/routes/services.py:66-109,188-207,226-234`, `equipment.py:34-43`, `invoices.py:152-157,227-230`, `dashboard.py:32-38`. Los modelos no usan FK compuestas empresariales; véase [05](05-modelo-datos.md).

### H05 — Uploads públicos y sesiones sin ciclo de vida — alta

**Confirmado:** alta/consulta/carga de sesiones y subida directa carecen de identidad, propietario y empresa. MIME se acepta por prefijo declarado; no hay límite aplicativo de tamaño, validación binaria, TTL, limpieza ni protección contra reuso. Archivos se sirven por StaticFiles públicamente. **Inferido:** crecimiento no acotado de disco/memoria y acceso a foto para quien conozca la URL; no se midieron límites del servidor o red. Evidencia: `backend/app/api/routes/uploads.py:16-118`, `backend/app/main.py:31`.

### H06 — Permisos declarados no equivalen a permisos efectivos — media

**Confirmado:** modulos_permitidos de Company no es consultado por autorización; Dashboard y notificaciones no comprueban permisos granulares. La UI usa defaults cuando permisos faltan, API rechaza; muchas acciones UI verifican roles rígidos. Ejemplos: vendedor tiene `servicios.ver/crear` en semilla pero no accede a `/servicios`; técnico tiene clientes.crear pero Clients no muestra alta; comprobantes.crear de vendedor no tiene punto de emisión en su pantalla. Evidencia: `backend/app/db/init_db.py:89-118`, `backend/app/api/deps.py:57-74`, `frontend/src/App.jsx:136-149`, `frontend/src/pages/Clients.jsx:58-61`, `frontend/src/pages/ServiceDetail.jsx:171`, `frontend/src/utils/permissions.js:69-72`.

## Consistencia de negocio y transacciones

### H07 — Cobros/correlativos/cupos expuestos a concurrencia — alta

**Confirmado:** registro de pago lee saldo sin bloqueo de orden, el correlativo usa máximo+1, cupo usa count seguido de INSERT. Solo consumo de producto bloquea fila. Índices únicos de comprobante limitan duplicación, pero no hay manejo de IntegrityError/reintento. **Inferido:** dos cobros pueden superar saldo; dos emisores pueden colisionar; altas simultáneas pueden superar cupo. No se ejecutaron pruebas de carga. Evidencia: `backend/app/api/routes/payments.py:128-183`, `invoices.py:56-74,244-288`, `users.py:60-86`, `services.py:207`.

### H08 — Código existente no conectado

**Confirmado mediante búsqueda de referencias en código propio:** Products.jsx no está importado en App; `/productos` usa Inventory. `components/ProtectedRoute.jsx` exporta Dashboard y consulta `/dashboard`, pero el guard usado está en App y la pantalla activa Dashboard consulta `/dashboard/stats`. RoleChecker y discount_inventory_for_service no tienen callers. En Services, handleNotify y handleStatusChange solo aparecen en sus declaraciones. Schemas InventoryMovementCreate/Response, ProductUpdate, InvoiceItemCreate y ServiceItemCreate no tienen endpoints que los consuman. **Límite:** no se afirma nada sobre importaciones de consumidores externos ausentes. Evidencia: `frontend/src/App.jsx:16-33,48-81,232-246`, `frontend/src/components/ProtectedRoute.jsx:17-46`, `frontend/src/pages/Dashboard.jsx:28`, `frontend/src/pages/Services.jsx:437-479`, `backend/app/core/rbac.py:6-21`, `backend/app/services/inventory_service.py:7-49`; inventario de imports/rutas en [06](06-apis-integraciones.md).

### H09 — Archivos vacíos y funcionalidades no implementadas

**Confirmado:** inventory.py de rutas, db/base.py, alembic/script.py.mako y components/Modal.jsx están vacíos. Los `__init__.py` vacíos son marcadores de paquete, no se clasifican por sí solos como defectos. No hay API de entradas/ajustes/listado de movimientos, edición/eliminación de productos, edición/eliminación de equipos ni retiro de items de orden. README menciona firmas, pero no se encontró contrato, campo, handler ni interfaz de firma. Evidencia: inventario con tamaños/huellas, `backend/app/main.py:41-54`, conjunto de rutas, modelos y schemas en [05](05-modelo-datos.md)/[06](06-apis-integraciones.md), `README.md:19`.

### H10 — Auditoría visual de demostración

**Confirmado:** Audit.jsx define cinco eventos fijos de septiembre de 2026, los filtra localmente y no importa api. Incluso muestra un evento ficticio de eliminar producto, operación no expuesta. El backend sí almacena eventos y ofrece GET `/audit/`. La pantalla no prueba que dichos eventos hayan ocurrido. Evidencia: `frontend/src/pages/Audit.jsx:14-65,125-138`; `backend/app/api/routes/audit.py:12-20`.

### H11 — log_audit confirma trabajo ajeno y eventos sin empresa — alta

**Confirmado:** auditoría hace commit sobre la sesión del caller. En consumo/comprobantes/notificación confirma negocio junto con evento; en otros CRUD llega después de uno o varios commits ya persistidos. Emisión/anulación de comprobantes omiten empresa_id, por lo que no aparecen para administrador empresarial. Notificación registra entidad Notification con ID de servicio. DELETE de licencia usa empresa del actor, no de licencia, relevante para SUPERADMIN. **Inferido:** fallo de auditoría puede dejar negocio confirmado con respuesta de error; trazas pueden quedar fuera del ámbito o asociadas a ID semánticamente equivocado. Evidencia: `backend/app/services/audit_service.py:5-23`, `backend/app/api/routes/invoices.py:273-285,326-336`, `backend/app/services/notification_service.py:19-24`, `backend/app/api/routes/licenses.py:199-206`.

### H12 — Estados de órdenes sin restricciones de transición

**Confirmado:** cualquier enum puede reemplazar otro, incluso reabrir CANCELADO/ENTREGADO; fecha final no se limpia. API permite consumir producto en órdenes cerradas, aunque UI lo oculta. Cancelar orden no repone stock ni anula pagos/documentos. Monto puede cambiar después de emitir comprobante: el snapshot no se recalcula. **Inferido:** orden, saldo e importe facturado pueden divergir según operaciones posteriores. Evidencia: `backend/app/api/routes/services.py:127-272`; `backend/app/api/routes/invoices.py:201-271`; `frontend/src/pages/ServiceDetail.jsx:113-117,303-306`.

### H13 — Comprobación parcial de valores y errores de integridad

**Confirmado:** mayoría de strings de entrada no tienen min/max; precios, stock y monto base no tienen restricciones de no negatividad en API/modelos. UI impone algunas. PUT de cliente/usuario no comprueba unicidad antes de commit; opcionales permiten null para columnas NOT NULL. No hay handler general de IntegrityError ni respuestas específicas para esos fallos. Serie de comprobante se valida antes de trim: una serie de espacios pasa longitud inicial y acaba vacía. Evidencia: `backend/app/schemas/client.py:5-23`, `user.py:10-26`, `product.py:5-25`, `service.py:10-28`, `invoice.py:32`, `backend/app/api/routes/invoices.py:214`; `backend/app/main.py:1-54`.

### H14 — Dashboard financiero difiere del saldo

**Confirmado:** ingresos_hoy suma todos los pagos de la fecha, incluidos ANULADO. El saldo usa solo PAGADO. Dashboard cuenta solo RECIBIDO como pendiente, EN_PROCESO como proceso y TERMINADO como terminado; Services agrupa también DIAGNOSTICO y ENTREGADO en otras métricas. UI de pagos considera servicio con total cero PENDIENTE; API de resumen lo considera PAGADO. Evidencia: `backend/app/api/routes/dashboard.py:24-30`, `payments.py:41-59`, `frontend/src/pages/Services.jsx:315-332`, `frontend/src/pages/Payments.jsx:241-249`.

### H15 — Licencias con validación desigual y estado derivado

**Confirmado:** PUT no repite validación fin≥inicio del schema de creación, ni comprueba dispositivos positivos. Categoría libre. No permanente sin fin resulta ACTIVA; inicio futuro no impide ACTIVA; vencimiento se calcula con fecha local del servidor, mientras otras fechas usan UTC. Las alertas solo se recalculan al consultar. Evidencia: `backend/app/schemas/license.py:8-32,34-45`, `backend/app/api/routes/licenses.py:16-31,152-166`.

## Interfaz y comunicación

### H16 — URLs de imágenes y captura móvil dependen del origen

**Confirmado:** API retorna `/static/uploads/...`, ImageUploadControl usa `src={value}` sin prefijo backend, Vite no configura proxy. QR usa hostname/protocolo/puerto del navegador y Axios usa localhost por defecto y Compose. **Inferido:** en topología estándar separada la vista previa pide el archivo al frontend; desde móvil localhost apunta al teléfono. Accesibilidad real de QR/imágenes depende de configuración externa no verificada. El servicio QR recibe la URL con ID de sesión. Evidencia: `backend/app/api/routes/uploads.py:49,114`, `frontend/src/components/ImageUploadControl.jsx:63-66,105-106,142-147`, `frontend/vite.config.js:4-13`, `docker-compose.yml:50`.

### H17 — Exportación OpenAPI desactualizada

**Confirmado:** 27 operaciones en archivo raíz frente a 42 decoradores montados; faltan 15 operaciones, incluidos empresas/licencias/uploads, roles/edición de usuarios y PDF. Faltan campos empresa/permisos/fotos en contratos compartidos. El detalle reproducible está en `contraste-openapi.json`; comparación de nombres de campos no equivale a comparación completa de validadores. Evidencia: `openapi.json:1`; `backend/app/main.py:41-54` y tabla [06](06-apis-integraciones.md).

### H18 — Navegación y controles sin implementación funcional

**Confirmado:** Sidebar enlaza `/notificaciones` pero App no registra esa ruta; el catch-all vuelve a `/`. Navbar búsqueda, campana y perfil no tienen handlers de negocio. Login «recordarme» solo cambia estado visual; AuthContext siempre usa localStorage. Evidencia: `frontend/src/components/Sidebar.jsx:134-139`, `frontend/src/App.jsx:334-342`, `frontend/src/components/Navbar.jsx:32-71`, `frontend/src/pages/Login.jsx:78`, `frontend/src/context/AuthContext.jsx:36-37`.

### H19 — Manejo de errores de usuarios referencia función inexistente

**Confirmado:** botón Reintentar usa `loadUsers`; la función declarada es `loadData`, sin definición/import de loadUsers. **Inferido:** cuando error es truthy, evaluar ese JSX puede lanzar ReferenceError y ocultar la recuperación visual. Evidencia: `frontend/src/pages/Users.jsx:55-75,279-284` y búsqueda de referencias en archivo completo.

### H20 — Clientes inactivos ausentes de las vistas dependientes

**Confirmado:** GET clientes siempre filtra activo=true, mientras la pantalla calcula un contador de inactivos sobre esa respuesta. Desactivar mediante PUT hace que el cliente desaparezca tras recargar; la UI no ofrece una consulta de inactivos para volver a seleccionarlo. Equipos y pagos resuelven nombres a partir de esa misma lista, por lo que conservan sus registros pero pueden mostrar etiquetas de cliente desconocido/ID. Reactivación sigue siendo posible por PUT si se conoce el ID. Evidencia: `backend/app/api/routes/clients.py:18-21,53-82`, `frontend/src/pages/Clients.jsx:106-112,243-259`, `frontend/src/pages/Equipment.jsx:156-190`, `frontend/src/pages/Payments.jsx:503-517`.

### H21 — Datos de cliente y campos de respuesta inconsistentes

**Confirmado:** Payments usa nombre/apellido/razon_social, pero ClientResponse usa nombres/apellidos; la búsqueda por nombres y etiquetas puede fallar o caer a email/ID. ServiceDetail espera cliente/equipo anidados, ausentes en ServiceResponse, y usa fallback por ID. ServiceUpdateStatus declara imagen_url y el handler no la aplica. Evidencia: `frontend/src/pages/Payments.jsx:276-280,503-517`, `backend/app/schemas/client.py:5-29`, `frontend/src/pages/ServiceDetail.jsx:482-505`, `backend/app/schemas/service.py:24-49`, `backend/app/api/routes/services.py:146-160`.

### H22 — Permisos locales obsoletos y registro de sesión en consola

**Confirmado:** AuthContext restaura JSON local sin consultar `/me`; cambios de rol/permiso no actualizan UI hasta otra acción de sesión. Services imprime user en console.log y ese objeto procede de respuesta de login que incluye access_token. **Inferido:** la consola puede contener token mientras la pantalla se renderiza; no se observó una sesión real. Backend sí relee User. Evidencia: `frontend/src/context/AuthContext.jsx:14-21,34-39,67-73`, `frontend/src/pages/Services.jsx:135`, `backend/app/api/routes/auth.py:42-51`, `backend/app/api/deps.py:26`.

### H23 — Alta de empresa manda email opcional vacío

**Confirmado:** Superadmin inicializa email_contacto a string vacío y envía formData sin convertirlo a null. Schema acepta EmailStr o null, no convierte explícitamente vacío. **Inferido:** dejarlo vacío puede producir validación 422; la UI coloca detail directamente como contenido y no transforma listas de errores en texto. No se ejecutó formulario. Evidencia: `frontend/src/pages/Superadmin.jsx:13-22,52,67`, `backend/app/schemas/company.py:37-48`.

### H24 — Páginas dependen de permisos de módulos auxiliares

**Confirmado:** Services carga clientes/equipos y, si ADMIN, usuarios; Payments requiere además servicios/clientes; Licenses requiere clientes/equipos. Promise.all rechaza la carga conjunta si falla una dependencia. Permiso ver del módulo principal por sí solo no garantiza carga de pantalla. Licenses/Superadmin solo registran en consola errores iniciales. Evidencia: `frontend/src/pages/Services.jsx:206-239`, `Payments.jsx:147-192`, `Licenses.jsx:53-68`, `Superadmin.jsx:25-34`.

## Esquema, despliegue y pruebas

### H25 — Migraciones no reproducen el esquema actual — alta

**Confirmado:** 0001 no crea tablas; 0002 presupone services/products; 0005 crea invoices sin empresa_id; no hay revisiones para cambios multiempresa/licencias/imágenes. Docker inicializa ORM y marca head sin upgrade. **Inferido:** base nueva por migraciones históricas y base antigua arrancada con create_all+stamp no son equivalentes al esquema ORM actual. Estado instalado desconocido. Evidencia: cinco revisiones, `backend/Dockerfile:21`, `backend/app/db/init_db.py:10`, [09](09-configuracion-despliegue.md).

### H26 — Alembic y aplicación pueden usar conexiones distintas — alta

**Confirmado:** Settings/Compose usan DATABASE_URL; env.py usa INI sqlalchemy.url sin sobrescribirlo. **Inferido:** personalizar PostgreSQL en Compose puede hacer que init_db tenga éxito y stamp falle o apunte a otra base. Evidencia: `docker-compose.yml:8-10,32`, `backend/alembic.ini:3`, `backend/alembic/env.py:60-94`.

### H27 — Semillas y alta empresarial no son atómicas

**Confirmado:** init_db confirma por partes y silencia excepciones SQL sin rollback. Crear empresa confirma antes de crear administrador. Defaults de JWT, conexión y passwords de demostración son literales. **Inferido:** fallo intermedio deja estado parcial; uso de defaults en despliegue conserva secretos conocidos del código. No se comprobó su uso efectivo. Evidencia: `backend/app/db/init_db.py:19-51,53-118,159-168`, `backend/app/api/routes/companies.py:74-98`, `backend/app/core/config.py:8-11`, `docker-compose.yml:33`.

### H28 — Runtime de desarrollo y configuración no probada

**Confirmado:** frontend arranca Vite dev; no hay proxy/TLS/CI/backup declarados. tailwind.config.cjs contiene `export default` mientras postcss.config.cjs usa module.exports. **Desconocido:** compatibilidad efectiva de ese export con el loader instalado; no se etiqueta como fallo de build sin ejecutarlo. Evidencia: `frontend/Dockerfile:12`, `frontend/tailwind.config.cjs:2`, `frontend/postcss.config.cjs:1-6`, inventario de configuración.

### H29 — Pruebas escasas y desalineadas

**Confirmado:** solo dos pruebas de login, con email que no coincide con la semilla actual. No hay fixtures/overrides, pruebas de aislamiento, stock, pagos, comprobantes ni scripts test frontend en la copia revisada. **Desconocido:** resultados en un entorno existente; no se ejecutaron para evitar carga de `.env` y escritura de auditoría. Evidencia: `backend/tests/test_main.py:1-22`, `backend/app/db/init_db.py:66-77`, `frontend/package.json:6-9`.

### H30 — Documentación comercial excede implementación

| Declaración o apariencia | Contraste confirmado | Evidencia |
|---|---|---|
| «Firmas» en servicios | Sin campo/contrato/flujo de firma encontrado | `README.md:19`; schemas/models/service y ServiceDetail |
| «Licencias» de plataforma y suscripciones | Company tiene cupo/activo/módulos; License almacena claves de software, no plan/vigencia SaaS ni cobro recurrente | `README.md:18`; `backend/app/models/company.py:10-20`; `license.py:13-31` |
| «Tiempo real» QR | Polling 1500 ms, sin WebSocket | `README.md:20`; `frontend/src/components/ImageUploadControl.jsx:78-103` |
| «Facturación» | Comprobantes internos; pie PDF lo aclara; no integración SUNAT | `README.md:23`; `backend/app/api/routes/invoices.py:1465-1469` |
| «Historial por cliente/equipo» | API servicios filtra cliente; no filtro equipo ni página de historial dedicada | `README.md:22`; `backend/app/api/routes/services.py:25-38`; `frontend/src/App.jsx:136-205` |
| «Notificación enviada» | Fila local ENVIADO sin envío externo | `backend/app/services/notification_service.py:10-26` |

## Incertidumbres y límites de cierre

| ID | Desconocido | Motivo / evidencia necesaria |
|---|---|---|
| U01 | Variables efectivas y credenciales en uso | `.env*` excluido por instrucción; no se consultó entorno secreto |
| U02 | Esquema/datos/versión Alembic de instancia instalada | No conexión a PostgreSQL ni introspección; se requeriría revisión autorizada de instancia |
| U03 | Build, render UI y compatibilidad exacta de paquetes | Dependencias instaladas excluidas; no npm/build/browser |
| U04 | Comportamiento concurrente y rendimiento | Hallazgos basados en orden de consultas/commits; sin carga experimental |
| U05 | Disponibilidad de QR, fondos y captura desde LAN | Solo URLs/configuración de código; no se contactó servicio externo |
| U06 | Infraestructura externa, TLS, backups, despliegue real | No aparece en copia local |
| U07 | Propósito empresarial exacto de estados y expectativas de auditoría | Código expresa operaciones, no política organizacional completa |
| U08 | Commit, autoría y evolución histórica | Copia sin repositorio Git utilizable; solo hashes de archivos |
| U09 | Contenido/consentimiento de fotos almacenadas | Dos JPG inventariados por nombre/tamaño sin abrir |
| U10 | Explotabilidad efectiva e impacto sobre información real | No pruebas activas ni acceso a usuarios/datos reales |

No quedan módulos de código propio identificados fuera del inventario. Estas incertidumbres impiden afirmar validación operativa o seguridad completa; no se convierten en funcionalidades implementadas ni se ocultan como «verificadas en producción». Consulte [trazabilidad](trazabilidad.md) para el alcance exacto de la revisión estática y las comprobaciones realizadas.
