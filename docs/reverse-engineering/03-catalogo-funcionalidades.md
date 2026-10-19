# Catálogo funcional reconstruido

Cada ficha describe código confirmado, sus recorridos y sus límites. Todos los endpoints de negocio están detallados en [06](06-apis-integraciones.md), con esquema de entrada/salida y dependencia de autorización. Las columnas exactas están en [05](05-modelo-datos.md). La palabra «permiso» en estas fichas se refiere al servidor; la UI puede restringir adicionalmente por rol.

## F01 — Identidad y sesión

**Propósito/actores:** iniciar sesión como SUPERADMIN, ADMIN, TECNICO o VENDEDOR; restaurar sesión local y salir. **Entrada:** `/login` en React, `POST /api/auth/login`, `GET /api/auth/me`.

**Recorrido:** `Login.handleSubmit` recorta email → `AuthProvider.login` envía JSON → `auth.login` consulta `users.email` → verifica hash y actividad → crea JWT → `log_audit` guarda LOGIN → devuelve identidad, empresa y permisos → navegador guarda `token` y `user` → navega a `/superadmin` o `/`. `/me` devuelve `UserResponse`, con rol como objeto, a diferencia del rol de texto del login. Logout elimina ambos valores locales. Un 401 en cualquier llamada Axios limpia sesión y fuerza `/login`.

**Datos y reglas:** email válido y password string; token bearer con expiración; consulta de User en cada petición protegida; bloqueo de empresa suspendida. **Errores:** 401 credenciales/token, 400 usuario inactivo, 403 empresa suspendida. No se implementan registro público, recuperación de contraseña, refresh token ni revocación por logout. `rememberMe` solo cambia un estado visual: no afecta la persistencia. **Dependencias:** config, bcrypt, jose, User/Role/Company, Audit, localStorage. **Evidencia:** `frontend/src/pages/Login.jsx:72-121`, `frontend/src/context/AuthContext.jsx:13-73`, `frontend/src/services/api.js:7-24`, `backend/app/api/routes/auth.py:13-56`, `backend/app/api/deps.py:12-39`.

## F02 — Empresas y administrador inicial

**Propósito/actor:** SUPERADMIN registra y suspende empresas. **Entrada:** `/superadmin`; API `/companies/`, PUT por ID y PATCH `toggle-status`.

**Recorrido de alta:** formulario envía empresa, cupo y credenciales iniciales → comprobar email de administrador globalmente único y existencia del rol ADMIN → insertar Company activa y confirmar → insertar User con bcrypt y confirmar → auditar CREAR_EMPRESA → devolver CompanyResponse con total_usuarios=1. El listado ordena por creación descendente y cuenta todos los usuarios de cada empresa con consultas separadas. PUT aplica solo campos enviados, vuelve a contar usuarios y audita. PATCH invierte `activo`, confirma y audita; siguientes peticiones de sus usuarios serán rechazadas por `get_current_user`.

**Datos/reglas:** nombre obligatorio, correo de contacto opcional validado, cupo por defecto 10; actualización admite `modulos_permitidos`. No hay comprobación de RUC único ni mínimo del cupo en servidor. **Errores/casos especiales:** 400 email duplicado, 500 rol ADMIN ausente, 404 empresa ausente; empresa puede quedar creada sin administrador si falla el segundo paso. La UI permite alta/suspensión y búsqueda local; no conecta el PUT de edición ni configura módulos. Su contador rotulado «Usuarios Activos» cuenta también inactivos. **BD/dependencias:** Company, User, Role, hash y Audit. **Evidencia:** `backend/app/api/routes/companies.py:16-199`, `backend/app/schemas/company.py:5-48`, `frontend/src/pages/Superadmin.jsx:13-91`, `frontend/src/pages/Superadmin.jsx:186-217`.

## F03 — Usuarios, roles y permisos

**Actores/entrada:** ADMIN de empresa y SUPERADMIN por API; pantalla `/usuarios` limitada a ADMIN. GET `/users/roles`, GET/POST `/users/`, PUT `/users/{user_id}`.

**Recorrido:** pantalla carga usuarios y roles en paralelo → crea formulario con permisos normalizados → valida nombre, email y contraseña mínima de seis caracteres en UI → POST/PUT. El servidor fija empresa del administrador (SUPERADMIN puede enviar otra), cuenta usuarios para comparar el cupo, rechaza email duplicado al crear, hashea contraseña, inserta y audita. PUT busca al usuario dentro del ámbito de empresa, reemplaza campos enviados, transforma contraseña no vacía a hash y recarga relación `rol`. Contraseña vacía no cambia hash. `activo` puede actualizarse por API, pero el formulario actual no lo envía.

**Datos/salida:** UserResponse con rol anidado y permisos JSON; nunca hash. Los roles listados a ADMIN excluyen SUPERADMIN, pero POST/PUT no restringen el `rol_id` destino. **Errores:** 400 cupo/email en creación, 404 usuario al editar; FK/duplicado de email en PUT sin traducción explícita. Cupo cuenta inactivos, sin bloqueo concurrente. **Dependencias:** Company/User/Role, schemas.user, security, log_audit, permissions.js. **Evidencia:** `backend/app/api/routes/users.py:14-137`, `frontend/src/pages/Users.jsx:55-220`, `backend/app/schemas/user.py:10-34`.

## F04 — Clientes, búsqueda y desactivación

**Actores/entrada:** permisos `clientes.ver/crear/editar`; UI muestra crear/editar a ADMIN y VENDEDOR. GET/POST `/clients/`, PUT por ID.

**Recorrido:** cargar activos de empresa → búsqueda local por nombres, documento, teléfono o email → formulario recorta textos y convierte email/dirección vacíos a null → POST comprueba documento por empresa → inserta y audita. Edición aplica campos presentes y permite `activo=false`; tras recargar desaparece del listado porque GET siempre filtra activos. React tiene contador de inactivos, pero no los recibe por esa ruta.

**Datos/reglas:** nombres, apellidos, documento y teléfono obligatorios en el schema; UI exige texto no vacío, servidor no impone longitud mínima. Unicidad `(empresa_id,documento)` en BD; comprobación preventiva solo en alta. **Errores:** 400 duplicado al crear, 404 edición ajena/inexistente; conflicto de unicidad al editar no se traduce. **BD/dependencias:** Client, Audit; consumido por equipos, servicios, licencias y pagos. No hay DELETE ni GET de cliente individual. **Evidencia:** `frontend/src/pages/Clients.jsx:55-266`, `backend/app/api/routes/clients.py:13-82`, `backend/app/models/client.py:9-27`, `backend/app/schemas/client.py:5-29`.

## F05 — Registro y consulta de equipos

**Actores/entrada:** `equipos.ver/crear`; `/equipos` y alta rápida en Servicios; GET/POST `/equipment/` (GET admite `cliente_id`).

**Recorrido:** Equipment carga equipos y clientes por separado, une por ID para presentar nombres y filtra localmente. Formulario exige cliente/tipo/marca/modelo, convierte ID a número y opcionales vacíos a null → API valida cliente dentro de empresa → inserta equipo → confirma/audita. La serie se indexa, no es única. El alta rápida desde Servicios crea un equipo de inmediato, lo selecciona y copia su foto al formulario; cancelar después la orden no elimina ese equipo.

**Salida/reglas:** EquipmentResponse con URL opcional de foto, sin entidad cliente anidada. No hay PUT/DELETE ni historial dedicado por equipo. **Errores:** 404 cliente ajeno/inexistente; errores de carga/formulario en UI. No se exige que el cliente esté activo. **BD/dependencias:** Equipment→Client y Company; ImageUploadControl opcional y Audit. **Evidencia:** `frontend/src/pages/Equipment.jsx:141-315`, `frontend/src/pages/Services.jsx:162-195`, `backend/app/api/routes/equipment.py:14-57`, `backend/app/models/equipment.py:13-25`.

## F06 — Crear, consultar y buscar órdenes

**Actores/entrada:** `servicios.ver/crear`; UI `/servicios` limitada a ADMIN/TECNICO. GET `/services/`, GET por ID y POST; listado admite `cliente_id`.

**Recorrido:** Services carga servicios/clientes/equipos con Promise.all y usuarios solo si ADMIN → filtra equipos por cliente → formulario acepta equipo y responsable opcionales → fecha estimada se convierte desde día local a ISO a las 23:59 → API valida cliente de empresa y, si hay equipo, pertenencia a ese cliente → copia foto al equipo si se proporcionó → crea Service RECIBIDO con monto base → confirma y audita → recarga listas. GET usa joinedload(items), orden descendente y filtro empresarial. Detalle carga además productos para resolver nombres y, solo ADMIN, lista comprobantes y busca por servicio.

**Datos/salida:** ServiceCreate/Response con IDs, descripción, tipo libre, monto, fechas, imagen e items. El responsable solo queda sujeto a FK: no se valida rol, actividad ni empresa. `monto` representa mano de obra/base y no incluye items. Tipos «Venta» y «Antivirus / Licencia» reutilizan la misma entidad; crear orden de software no crea una License. ServiceResponse no anida cliente/equipo: el detalle usa etiquetas por ID. **Errores:** 404 cliente/servicio, 400 equipo incompatible; si falla una carga de Promise.all no se actualizan listas. **Dependencias:** Client, Equipment, User, Service, ServiceItem, Audit; productos y comprobantes en detalle. **Evidencia:** `frontend/src/pages/Services.jsx:206-435`, `frontend/src/pages/ServiceDetail.jsx:173-259`, `frontend/src/pages/ServiceDetail.jsx:482-505`, `backend/app/api/routes/services.py:25-125`, `backend/app/schemas/service.py:10-49`.

## F07 — Diagnóstico y estados de una orden

**Entrada/actor:** botón guardar del detalle → PATCH `/services/{id}/status`, permiso `servicios.editar`.

**Recorrido:** UI envía enum estado y diagnóstico solo si no está vacío → API busca servicio de empresa → asigna estado y, cuando no son null, diagnóstico/monto → TERMINADO o ENTREGADO escribe fecha_finalizacion actual UTC → confirma y audita. Puede enviarse el mismo estado repetidamente. No hay matriz de transiciones; se puede volver desde CANCELADO/ENTREGADO a cualquier enum. Volver a un estado abierto no limpia la fecha final.

**Efectos/límites:** no devuelve stock, anula pagos, emite comprobantes ni notifica automáticamente. Schema acepta imagen_url pero handler no la usa. UI no ofrece edición del monto en este recorrido y no permite borrar diagnóstico enviando vacío, aunque API acepta string vacío. Los helpers `handleStatusChange` y `handleNotify` de la lista no están enlazados desde el JSX. **Errores:** 404 servicio, 422 estado fuera del enum. **BD/dependencias:** Service y Audit; get_current_user/check_permission. **Evidencia:** `backend/app/api/routes/services.py:127-173`, `backend/app/schemas/service.py:24-28`, `frontend/src/pages/ServiceDetail.jsx:261-301`, `frontend/src/pages/Services.jsx:437-479`.

## F08 — Catálogo, stock inicial y consumo de productos

**Actores/entrada:** `productos.ver/crear` para catálogo; `servicios.editar` para consumo. `/productos` muestra Inventory.jsx. GET/POST `/products/`; POST `/services/{id}/products`.

**Catálogo:** carga productos activos, busca nombre/código/categoría, calcula unidades y stock bajo/sin stock. Alta UI solo ADMIN: exige stock y mínimo enteros no negativos, precios finitos no negativos y textos no vacíos. API solo comprueba código duplicado por empresa y tipos del schema; crea stock inicial sin movimiento ENTRADA y audita. ProductUpdate existe pero no hay ruta de edición. Products.jsx contiene otra vista con valorización `stock*precio_compra`, no conectada a App.

**Consumo:** seleccionar producto y cantidad → UI exige entero positivo y stock suficiente → API repite cantidad positiva, valida servicio y producto activo del ámbito, bloquea Product → comprueba stock → toma precio_venta vigente → calcula subtotal → resta stock → crea InventoryMovement SALIDA y ServiceItem con precio histórico → log_audit confirma todo → devuelve mensaje, detalle y stock_actual → UI recarga servicio/productos. Agregar nuevamente el mismo producto crea otra línea. No hay retirar item ni restitución automática al cancelar orden. La UI oculta agregar en ENTREGADO/CANCELADO; API no comprueba esos estados.

**Errores:** 400 duplicado/cantidad/stock, 404 servicio/producto. **Dependencias:** Product, Service, ServiceItem, InventoryMovement, Audit; rutina `discount_inventory_for_service` desconectada. No existe consulta ni mantenimiento general de movimientos: router inventory.py vacío y no registrado. **Evidencia:** `frontend/src/pages/Inventory.jsx:100-267`, `frontend/src/App.jsx:232-246`, `backend/app/api/routes/products.py:13-51`, `backend/app/api/routes/services.py:175-272`, `frontend/src/pages/ServiceDetail.jsx:303-405`, `backend/app/services/inventory_service.py:7-49`.

## F09 — Pagos, saldos y anulación

**Actores/entrada:** `pagos.ver/crear/editar`; UI ADMIN/VENDEDOR para cobrar, solo ADMIN para anular. GET/POST `/payments/`, GET `/payments/service/{id}`, PATCH `/{id}/anular`.

**Recorrido de consulta:** pantalla carga pagos, órdenes y clientes en paralelo; suma solo PAGADO y arma saldo/estado en navegador. API de resumen calcula con Decimal a dos decimales HALF_UP: total = base + suma de subtotales; pagado = suma de pagos PAGADO; saldo = máximo(total−pagado,0). Estado PAGADO si saldo≤0, PARCIAL si hay pago, en otro caso PENDIENTE. La pantalla usa regla distinta para total cero: exige total>0 para PAGADO.

**Registro:** formulario ofrece órdenes con saldo positivo no canceladas; limita importe al saldo visible → POST vuelve a consultar orden, impide CANCELADO y valida monto redondeado positivo ≤ saldo → inserta Payment PAGADO con empresa de la orden y usuario actual → confirma/audita → recarga. **Anulación:** confirmación visual → API encuentra pago de empresa y rechaza si ya ANULADO → cambia estado, confirma/audita. No elimina registro ni revierte una transferencia real. No actualiza Invoice ni estado de Service.

**Datos/errores:** método enum EFECTIVO/YAPE/PLIN/TRANSFERENCIA/TARJETA/OTRO; monto `gt=0` en schema y control posterior tras redondeo. 400 cancelación/repetición/exceso; 404 recurso. No hay bloqueo de saldo entre cobros simultáneos. Pagos usa `client.nombre`/`apellido`, mientras API devuelve `nombres`/`apellidos`; puede mostrar email o ID. **BD/dependencias:** Service.items/pagos, Payment, User, Audit; sin pasarela externa. **Evidencia:** `backend/app/api/routes/payments.py:21-236`, `backend/app/schemas/payment.py:8-38`, `frontend/src/pages/Payments.jsx:147-543`.

## F10 — Emitir, consultar y anular comprobantes

**Actores/entrada:** permisos `comprobantes.ver/crear/editar`; emisión visible solo ADMIN dentro del detalle de orden, lista `/comprobantes` también para VENDEDOR. GET/POST `/invoices/`, GET por ID y PATCH `anular`.

**Emisión:** UI elige BOLETA/B001, FACTURA/F001 o NOTA_VENTA/NV01 y observaciones → API busca orden e items, rechaza cancelada y cualquier comprobante previo (también anulado), consulta cliente, calcula base+productos → normaliza serie con trim/upper → busca mayor número por empresa/tipo/serie y suma uno → crea cabecera con snapshot de nombre/documento/dirección e importes → flush para ID → añade mano de obra si positiva y cada producto con concepto `Producto #ID` → audita/commit → responde con detalles. No exige orden pagada ni terminada; no calcula impuestos o descuentos ni consume inventario adicional.

**Consulta/anulación:** listado descendente; detalle incluye líneas; pantalla busca/filtra localmente y suma emitidos. Anular cambia solo estado, audita y conserva el documento; no libera la unicidad por servicio ni devuelve pagos/productos. **Errores:** 400 cancelado/duplicado/ya anulado, 404 recurso; serie longitud 1–10 antes de trim, sin patrón por tipo; conflictos concurrentes quedan sujetos a índices y no se capturan. **BD/dependencias:** Invoice/InvoiceItem, Service/ServiceItem, Client, Audit. **Evidencia:** `backend/app/api/routes/invoices.py:49-341`, `backend/app/models/invoice.py:27-69`, `backend/app/schemas/invoice.py:29-72`, `frontend/src/pages/ServiceDetail.jsx:511-658`, `frontend/src/pages/Invoices.jsx:291-470`.

## F11 — Descargar PDF de comprobante

**Entrada/actor:** botón de detalle de comprobante → GET `/invoices/{id}/pdf`, `comprobantes.ver`.

**Recorrido:** API consulta Invoice con detalles/cliente/servicio → ReportLab construye A4 en BytesIO con marca SIGES, número a seis dígitos, fecha/estado, datos históricos de cliente, descripción actual del servicio, líneas, totales y observaciones → escapa contenido de usuario para Paragraph → `document.build` → StreamingResponse PDF attachment. Axios solicita blob, crea ObjectURL y enlace download, pulsa y libera URL.

**Efectos/límites:** no guarda PDF ni escribe BD. Se permite generar uno anulado. Texto final indica que es comprobante interno/comercial y no validación SUNAT. La consulta de esta ruta no filtra empresa (H01). La descripción del servicio se lee actual, mientras cliente/importes son snapshot. **Errores:** 404 comprobante; fallos de generación sin manejador específico; UI muestra mensaje genérico. **Dependencias:** ReportLab, ORM, BytesIO, navegador. **Evidencia:** `backend/app/api/routes/invoices.py:348-1494`, `frontend/src/pages/Invoices.jsx:347-394`.

## F12 — Gestión de licencias de software

**Actores/entrada:** permisos `licencias.ver/crear/editar/eliminar`; `/licencias`; GET/POST `/licenses/`, PUT/DELETE por ID.

**Recorrido:** UI carga licencias, clientes y equipos; busca producto/clave/cliente/proveedor y filtra categoría localmente. API también admite filtros categoria y cliente_id, carga relaciones y agrega nombres/estado/días restantes. Alta valida ANTIVIRUS no permanente y fechas obligatorias; si no permanente y ambas fechas presentes, fin no anterior a inicio. Comprueba pertenencia de cliente y equipo individualmente, convierte categoría a mayúsculas, inserta y audita. No comprueba que equipo corresponda al cliente. PUT aplica campos enviados; solo repite regla de antivirus, sin validación de relaciones ni orden de fechas. DELETE elimina físicamente y audita.

**Vencimiento:** permanente → PERMANENTE y días null; con fin: delta<0 VENCIDA, 0..30 POR_VENCER, >30 ACTIVA; sin fin → ACTIVA/días null. Usa `date.today()` del servidor, sin comprobar inicio futuro. Alerta de pantalla calculada al cargar, sin programación de avisos. Clave visible y copiable al portapapeles; no hay cifrado aplicativo de ese campo. **Errores:** 422 validador de alta, 400 antivirus al editar, 404 pertenencia/recurso; error de carga solo console.error. **BD/dependencias:** License, Client, Equipment, Audit, clipboard. **Evidencia:** `backend/app/api/routes/licenses.py:16-207`, `backend/app/schemas/license.py:18-45`, `frontend/src/pages/Licenses.jsx:53-223`.

## F13 — Fotografías locales y captura móvil por QR

**Actores/entrada:** usuario del formulario de equipo/servicio y persona que posee el enlace móvil. Las cuatro rutas `/uploads` y lectura `/static` no requieren login.

**Directa:** navegador comprueba MIME image/*, envía multipart campo file → API comprueba prefijo image/ declarado, conserva extensión y genera UUID → lee todo y escribe en static/uploads → devuelve URL relativa y filename → onChange deja URL en formulario, persistida solo al guardar equipo/servicio. Quitar foto limpia campo local, no borra archivo.

**QR:** PC crea sesión UUID/PENDING con fecha en diccionario → construye enlace con origen actual y `/captura-movil/ID` → solicita imagen QR a qrserver con enlace completo → móvil selecciona/captura foto y vista previa FileReader → envía multipart de sesión → API comprueba existencia, escribe archivo `qr_ID_UUID.ext`, marca COMPLETED/photo_url → PC consulta cada 1500 ms y al completarse actualiza campo y cierra modal tras 1200 ms. Sesión no expira por tiempo ni se consume; puede recibir otra foto. Reinicio borra sesiones; procesos distintos no comparten diccionario.

**Errores/límites:** 400 MIME, 404 sesión ausente, 500 disco. No hay límite de tamaño ni validación binaria de imagen en el código. No hay asociación empresa/usuario en sesión. El servicio QR recibe el identificador en la URL; la configuración localhost no garantiza uso desde otro dispositivo. URL de imagen relativa se usa directamente por el frontend, cuyo servidor no define proxy static. **Dependencias:** disco, memoria, qrserver, Axios, FileReader y HTML capture; ver H05/H16. **Evidencia:** `backend/app/api/routes/uploads.py:11-118`, `backend/app/main.py:31`, `frontend/src/components/ImageUploadControl.jsx:26-147`, `frontend/src/pages/MobileCameraUpload.jsx:16-58`.

## F14 — Dashboard y métricas

**Actor/entrada:** usuario autenticado; `/` → GET `/dashboard/stats`.

**Recorrido:** seis agregaciones ORM cuentan clientes activos, servicios RECIBIDO/EN_PROCESO/TERMINADO, productos activos con stock≤mínimo y suman pagos del día UTC → aplican empresa si usuario no SUPERADMIN y empresa_id verdadero → devuelven seis números → tarjetas. No verifica permisos de módulos financieros. El monto diario incluye pagos ANULADO; estados de órdenes se cuentan individualmente y no coinciden con agrupaciones más amplias de la lista de Servicios. Usuario no SUPERADMIN sin empresa obtiene agregaciones globales por esa condición.

**Efectos/errores/dependencias:** solo SELECT; frontend carga una vez y muestra fallo; sin estadísticas históricas ni gráficos con datos adicionales. Payment, Product, Service y Client. **Evidencia:** `backend/app/api/routes/dashboard.py:16-54`, `backend/app/schemas/dashboard.py:3-9`, `frontend/src/pages/Dashboard.jsx:15-130`, `frontend/src/pages/Services.jsx:315-332`.

## F15 — Auditoría y notificaciones internas

**Auditoría:** routers invocan `log_audit` con acción, entidad, ID y descripción; guarda Audit y confirma la sesión. GET `/audit/` exige ADMIN/SUPERADMIN, filtra empresa salvo SUPERADMIN y devuelve últimos 100 por ID. La UI `/auditoria` usa cinco eventos hardcodeados, búsqueda local y métricas de esa muestra; no llama a esa API. En emisión/anulación de comprobante no se pasa empresa_id; tales registros son null y quedan fuera del listado empresarial. Notificación usa entidad Notification con entidad_id del servicio, no del registro creado.

**Notificación:** POST `/notifications/send` con servicio_id/mensaje requiere cualquier usuario autenticado → encuentra servicio de su empresa → `NotificationService` crea fila tipo INTERNA/estado ENVIADO → audita y confirma → respuesta NotificationResponse. No entrega correo, SMS, WhatsApp ni notificación push. No hay listado de notificaciones ni ruta React `/notificaciones`; el menú contiene ese enlace. El helper de envío en Services no tiene llamada desde su JSX.

**Errores/BD/dependencias:** notificación 404 servicio; validación de strings sin min/max en schema, pero DB tiene longitudes; auditoría sin paginación pública. Notification→Service/Client y Audit→User/Company. **Evidencia:** `backend/app/services/audit_service.py:5-23`, `backend/app/api/routes/audit.py:12-20`, `frontend/src/pages/Audit.jsx:14-138`, `backend/app/api/routes/notifications.py:12-34`, `backend/app/services/notification_service.py:5-26`, `frontend/src/components/Sidebar.jsx:134-139`.

## F16 — Navegación, filtros y estados visuales

**Recorrido:** App anida rutas en Layout, que combina Sidebar/Navbar/Outlet; Sidebar filtra enlaces por rol y permiso. Ruta desconocida redirige al dashboard. Los formularios usan modales definidos en páginas o JSX local, no el archivo vacío Modal.jsx. Carga, búsqueda, filtros y contadores se implementan localmente con hooks; la API de listados devuelve colecciones completas, excepto auditoría limitada a 100. No hay paginación remota en los endpoints registrados.

La búsqueda global, campana y botón de perfil de Navbar carecen de acción; logout y apertura del menú móvil sí funcionan por callbacks. Login incorpora carrusel de imágenes externas cada 5.5 segundos, mostrar/ocultar contraseña y checkbox de recuerdo sin efecto persistente. **Dependencias/efectos:** localStorage y estado React, sin tablas propias. **Evidencia:** `frontend/src/App.jsx:48-348`, `frontend/src/components/Layout.jsx:6-32`, `frontend/src/components/Navbar.jsx:25-79`, `frontend/src/components/Sidebar.jsx:154-171`, `frontend/src/pages/Login.jsx:76-121`.

## F17 — Inicialización, ejecución y pruebas existentes

Compose espera PostgreSQL saludable; backend ejecuta `init_db`, luego `alembic stamp head` y Uvicorn. Init registra tablas, roles, empresa Demo ID 1, usuarios por email y un producto/licencia si no existen. Las semillas usan varios commits e intentos de reajustar secuencias con excepciones silenciadas; no forman una única transacción idempotente comprobada. Frontend ejecuta Vite de desarrollo. Dos tests ejercitan login con email distinto de la semilla actual, sin fixtures/DB aislada. No se ejecutaron porque importar app carga Settings con env_file y login escribe auditoría. **Evidencia:** `docker-compose.yml:22-57`, `backend/Dockerfile:21`, `backend/app/db/init_db.py:9-174`, `backend/tests/test_main.py:1-22`. Detalle operativo en [09](09-configuracion-despliegue.md).
