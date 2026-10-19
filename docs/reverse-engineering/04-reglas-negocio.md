# Reglas de negocio y validaciones reales

Las reglas siguientes están confirmadas por lectura. «UI» es una restricción de formulario, no una garantía del servidor. Los riesgos derivados se separan en [hallazgos](10-hallazgos-incertidumbres.md).

| ID | Regla y ubicación efectiva | Consecuencia/caso especial | Evidencia |
|---|---|---|---|
| R01 | Login verifica email, bcrypt y usuario activo | Email global; 401 credenciales, 400 inactivo | `backend/app/api/routes/auth.py:15-22` |
| R02 | Empresa inactiva impide login y peticiones protegidas | Se consulta estado actual, no solo claim | `backend/app/api/routes/auth.py:25-29`; `backend/app/api/deps.py:32-37` |
| R03 | ADMIN/SUPERADMIN pasan permisos granulares automáticamente | Permisos false no les retiran acceso backend | `backend/app/api/deps.py:57-74` |
| R04 | Otros roles requieren permiso booleano exactamente true | Sin diccionario no hay permisos por defecto en API | `backend/app/api/deps.py:64-72` |
| R05 | UI usa permisos predeterminados si user.permisos es falsy | Puede mostrar acciones que API rechaza | `frontend/src/utils/permissions.js:15-22,69-72` |
| R06 | Muchos módulos excluyen SUPERADMIN en rutas React | API global disponible no equivale a pantalla disponible | `frontend/src/App.jsx:136-299` |
| R07 | Alta de usuario comprueba límite de empresa | Cuenta activos e inactivos; solo si empresa existe | `backend/app/api/routes/users.py:60-69` |
| R08 | Alta de usuario impide email duplicado | PUT no comprueba antes del commit; BD unique global | `backend/app/api/routes/users.py:71-86,115-124`; `backend/app/models/user.py:13` |
| R09 | Cambio de password no vacío se hashea; vacío se ignora | Mínimo seis caracteres solo UI, no schema | `backend/app/api/routes/users.py:115-119`; `frontend/src/pages/Users.jsx:158-165`; `backend/app/schemas/user.py:16-26` |
| R10 | Rol destino de usuario se asigna por rol_id | GET roles filtra SUPERADMIN, POST/PUT no lo restringen | `backend/app/api/routes/users.py:21-22,75-82,121-122` |
| R11 | Empresa nueva queda activa con administrador ADMIN | Comprobación de email y rol antes; commits separados | `backend/app/api/routes/companies.py:49-98` |
| R12 | Cupo de empresa y módulos son editables por API | No mínimo de cupo en schema ni aplicación de módulos al autorizar | `backend/app/schemas/company.py:17-25`; `backend/app/api/routes/companies.py:126-131`; `backend/app/api/deps.py:57-74` |
| R13 | Clientes listados deben estar activos | Desactivado no aparece para reactivarlo desde lista | `backend/app/api/routes/clients.py:18-21,68-72` |
| R14 | Documento de cliente único por empresa | Alta 400; índice también protege edición/concurrencia | `backend/app/api/routes/clients.py:29-35`; `backend/app/models/client.py:9-11` |
| R15 | Equipo debe referir cliente del ámbito | No exige cliente activo ni serie única | `backend/app/api/routes/equipment.py:34-43`; `backend/app/models/equipment.py:19` |
| R16 | Orden requiere cliente; equipo es opcional | Si existe equipo, debe corresponder al cliente | `backend/app/api/routes/services.py:68-94`; `backend/app/schemas/service.py:10-21` |
| R17 | Responsable de orden no recibe validación de negocio | FK verifica existencia, no rol/empresa/actividad | `backend/app/api/routes/services.py:99-109`; `backend/app/models/service.py:36` |
| R18 | Foto proporcionada al crear orden también actualiza equipo | Si equipo existe y URL es no vacía; solo URL, no binario | `backend/app/api/routes/services.py:96-108` |
| R19 | Estado inicial RECIBIDO; siete valores permitidos | Enum no define transiciones | `backend/app/models/service.py:16-23,40`; `backend/app/api/routes/services.py:146-158` |
| R20 | TERMINADO/ENTREGADO sobrescriben fecha final UTC | Reapertura no limpia fecha; repetición la vuelve a escribir | `backend/app/api/routes/services.py:154-158` |
| R21 | Diagnóstico/monto actualizan solo si no son null | API acepta monto negativo; UI de alta lo rechaza | `backend/app/api/routes/services.py:148-152`; `backend/app/schemas/service.py:21,27`; `frontend/src/pages/Services.jsx:384-389` |
| R22 | Stock y precios no negativos se validan en UI de catálogo | No Field ge/gt ni CHECK equivalente en Product | `frontend/src/pages/Inventory.jsx:195-238`; `backend/app/schemas/product.py:5-12`; `backend/app/models/product.py:19-22` |
| R23 | Código de producto único por empresa | Producto nuevo incluye stock, sin movimiento de entrada | `backend/app/api/routes/products.py:29-50`; `backend/app/models/product.py:9-11` |
| R24 | Consumo exige cantidad>0, producto activo y stock suficiente | Bloquea fila de producto; descuento y detalle en misma sesión | `backend/app/api/routes/services.py:182-258` |
| R25 | Precio del item = precio_venta en momento del consumo | Subtotal calculado como float*cantidad y persistido Numeric | `backend/app/api/routes/services.py:221-242` |
| R26 | UI no permite abrir consumo en ENTREGADO/CANCELADO | API sí carece de condición de estado | `frontend/src/pages/ServiceDetail.jsx:113-117,303-306`; `backend/app/api/routes/services.py:175-272` |
| R27 | Total de servicio = monto base + sum(items.subtotal) | No se modifica Service.monto al agregar producto | `backend/app/api/routes/payments.py:27-39`; `backend/app/api/routes/services.py:221-245` |
| R28 | Total pagado suma solo PAGADO | ANULADO permanece en historial, sin impacto en saldo | `backend/app/api/routes/payments.py:41-47,215-223` |
| R29 | Dinero se redondea a 0.01 HALF_UP en pagos/facturación | Pago >0 antes y después de redondear | `backend/app/api/routes/payments.py:21-25,155-161`; `backend/app/schemas/payment.py:10` |
| R30 | Cobro no puede exceder saldo ni referir orden CANCELADO | No requiere TERMINADO/ENTREGADO; no hay bloqueo del saldo | `backend/app/api/routes/payments.py:128-179` |
| R31 | Estado financiero calculado: PAGADO si saldo≤0, PARCIAL si hay abono, PENDIENTE si no | API considera total cero PAGADO; UI exige total>0 | `backend/app/api/routes/payments.py:49-59`; `frontend/src/pages/Payments.jsx:241-249` |
| R32 | Anular pago ya anulado produce 400 | No hay devolución externa ni cambio del comprobante | `backend/app/api/routes/payments.py:197-236` |
| R33 | Un comprobante por servicio, incluso anulado | Unicidad en BD y chequeo sin filtrar estado | `backend/app/models/invoice.py:36`; `backend/app/api/routes/invoices.py:174-187` |
| R34 | No emitir sobre orden CANCELADO | No valida pago completo, RUC del cliente ni tipo fiscal | `backend/app/api/routes/invoices.py:153-242`; `backend/app/schemas/invoice.py:29-33` |
| R35 | Serie trim+upper; siguiente número=max anterior+1 por empresa/tipo/serie | Sin secuencia/bloqueo específico; longitud se valida antes de trim | `backend/app/api/routes/invoices.py:56-74,214-221`; `backend/app/schemas/invoice.py:32` |
| R36 | Total y subtotal del comprobante son iguales | No impuestos/descuentos; mano de obra en detalle solo si >0 | `backend/app/api/routes/invoices.py:201-271` |
| R37 | Datos del cliente y precios quedan copiados en comprobante | PDF mezcla snapshot con descripción actual del servicio | `backend/app/api/routes/invoices.py:223-269,844-847,938-945` |
| R38 | Anulación de comprobante solo cambia estado | No reabre numeración ni anula pagos ni repone stock | `backend/app/api/routes/invoices.py:297-341` |
| R39 | ANTIVIRUS no puede ser permanente y necesita inicio/fin | Alta: 422 Pydantic; edición: 400 HTTPException | `backend/app/schemas/license.py:18-32`; `backend/app/api/routes/licenses.py:159-164` |
| R40 | Alta de licencia no permanente exige fin≥inicio cuando ambas existen | Edición no repite orden de fechas; categoría libre string | `backend/app/schemas/license.py:8,28-30,34-45` |
| R41 | Vencimiento usa diferencia con date.today | Día final pertenece a POR_VENCER; inicio futuro no altera estado | `backend/app/api/routes/licenses.py:16-31` |
| R42 | Licencia opcionalmente asociada a cliente/equipo | Alta verifica cada uno por empresa; PUT no; no valida correspondencia cliente-equipo | `backend/app/api/routes/licenses.py:90-117,144-164` |
| R43 | Cantidad de dispositivos default 1 | Sin gt=0 en API/modelo; min=1 solo input UI | `backend/app/schemas/license.py:11`; `backend/app/models/license.py:21`; `frontend/src/pages/Licenses.jsx:585` |
| R44 | Upload acepta MIME declarado que empieza image/ | No inspección de contenido, límite ni lista de extensiones | `backend/app/api/routes/uploads.py:29-42,94-107` |
| R45 | Sesiones QR PENDING→COMPLETED | Sin expiración/propietario/consumo único/limpieza | `backend/app/api/routes/uploads.py:16,52-118` |
| R46 | Dashboard suma pagos de fecha UTC actual | Incluye ANULADO, no exige permiso pagos.ver | `backend/app/api/routes/dashboard.py:19,29-38` |
| R47 | Auditoría devuelve 100 más recientes por ID | Ámbito de empresa, sin paginación/filtros públicos | `backend/app/api/routes/audit.py:17-20` |
| R48 | Notificación requiere servicio del ámbito | Basta autenticación; ENVIADO es estado local | `backend/app/api/routes/notifications.py:16-33`; `backend/app/services/notification_service.py:10-24` |
| R49 | log_audit confirma la sesión recibida | Puede confirmar cambios de negocio pendientes del caller | `backend/app/services/audit_service.py:14-23` |
| R50 | EmailStr valida formato en schemas de identidad/contacto | No valida existencia de buzón; cadena vacía no equivale a null | `backend/app/schemas/auth.py:15-17`; `backend/app/schemas/company.py:17-48`; `frontend/src/pages/Superadmin.jsx:13-22,52` |

## Enumeraciones y estados

| Dominio | Valores persistidos/aceptados | Evidencia |
|---|---|---|
| Roles sembrados | SUPERADMIN, ADMIN, TECNICO, VENDEDOR | `backend/app/db/init_db.py:16` |
| Servicio | RECIBIDO, DIAGNOSTICO, EN_PROCESO, ESPERA, TERMINADO, ENTREGADO, CANCELADO | `backend/app/models/service.py:16-23` |
| Movimiento | ENTRADA, SALIDA; solo SALIDA conectada a consumo | `backend/app/models/inventory.py:8-10`; `backend/app/api/routes/services.py:226-234` |
| Pago método | EFECTIVO, YAPE, PLIN, TRANSFERENCIA, TARJETA, OTRO | `backend/app/models/payment.py:8-14` |
| Pago estado | PAGADO, ANULADO | `backend/app/models/payment.py:16-18` |
| Comprobante tipo | BOLETA, FACTURA, NOTA_VENTA | `backend/app/models/invoice.py:18-21` |
| Comprobante estado | EMITIDO, ANULADO | `backend/app/models/invoice.py:23-25` |
| Licencia categoría | String libre normalizado uppercase; UI sugiere ANTIVIRUS/OFFICE/WINDOWS/OTROS | `backend/app/api/routes/licenses.py:109,154-157`; `frontend/src/pages/Licenses.jsx:318` |
| Licencia vencimiento | ACTIVA, POR_VENCER, VENCIDA, PERMANENTE; calculado, no columna | `backend/app/api/routes/licenses.py:16-60` |
| Notificación | Tipo/estado string; flujo actual INTERNA/ENVIADO | `backend/app/models/notification.py:17-19`; `backend/app/services/notification_service.py:14-16` |
