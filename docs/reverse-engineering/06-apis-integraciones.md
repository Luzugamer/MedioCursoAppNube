# API e integraciones

## Convenciones y alcance

Base predeterminada `/api`, configurable por API_V1_STR (`backend/app/core/config.py:7`); routers montados en `backend/app/main.py:41-54`. Son 42 operaciones HTTP de negocio. Se conservan barras finales. JSON en cuerpos de negocio; uploads usa multipart `file`; PDF devuelve application/pdf. No se levantó el servidor ni se cargó `.env`.

`check_permission(m,a)` admite ADMIN/SUPERADMIN y, para otros roles, exige permiso explícito. `require_admin` admite esos dos roles; `require_superadmin` solo SUPERADMIN. `get_current_user` exige token/usuario/empresa activos. Sin dependencia de usuario significa público. Evidencia: `backend/app/api/deps.py:12-74`.

Tipos Pydantic, enums y Field producen validación previa al handler; errores de negocio y persistencia se describen por funcionalidad en [03](03-catalogo-funcionalidades.md). Los handlers sin `response_model` devuelven diccionarios, PDF o respuesta vacía según código; no se inventa un esquema.

## Operaciones vigentes

| Método y ruta | Función y evidencia | Parámetros (incluye body/query/path) | Control de acceso | Respuesta / éxito |
|---|---|---|---|---|
| `GET /api/audit/` | `get_audit_logs` — [backend/app/api/routes/audit.py:13](../../backend/app/api/routes/audit.py) | `—` | `Depends(require_admin)` | `List[AuditResponse]` / `200` |
| `POST /api/auth/login` | `login` — [backend/app/api/routes/auth.py:14](../../backend/app/api/routes/auth.py) | `login_req: LoginRequest` | `Público` | `Token` / `200` |
| `GET /api/auth/me` | `get_me` — [backend/app/api/routes/auth.py:55](../../backend/app/api/routes/auth.py) | `—` | `Depends(get_current_user)` | `UserResponse` / `200` |
| `GET /api/clients/` | `get_clients` — [backend/app/api/routes/clients.py:14](../../backend/app/api/routes/clients.py) | `—` | `Depends(check_permission('clientes', 'ver'))` | `List[ClientResponse]` / `200` |
| `POST /api/clients/` | `create_client` — [backend/app/api/routes/clients.py:24](../../backend/app/api/routes/clients.py) | `client_in: ClientCreate` | `Depends(check_permission('clientes', 'crear'))` | `ClientResponse` / `status.HTTP_201_CREATED` |
| `PUT /api/clients/{client_id}` | `update_client` — [backend/app/api/routes/clients.py:54](../../backend/app/api/routes/clients.py) | `client_id: int; client_in: ClientUpdate` | `Depends(check_permission('clientes', 'editar'))` | `ClientResponse` / `200` |
| `GET /api/companies/` | `get_companies` — [backend/app/api/routes/companies.py:17](../../backend/app/api/routes/companies.py) | `—` | `Depends(require_superadmin)` | `List[CompanyResponse]` / `200` |
| `POST /api/companies/` | `create_company_with_admin` — [backend/app/api/routes/companies.py:44](../../backend/app/api/routes/companies.py) | `comp_in: CompanyWithAdminCreate` | `Depends(require_superadmin)` | `CompanyResponse` / `status.HTTP_201_CREATED` |
| `PUT /api/companies/{company_id}` | `update_company` — [backend/app/api/routes/companies.py:116](../../backend/app/api/routes/companies.py) | `company_id: int; comp_in: CompanyUpdate` | `Depends(require_superadmin)` | `CompanyResponse` / `200` |
| `PATCH /api/companies/{company_id}/toggle-status` | `toggle_company_status` — [backend/app/api/routes/companies.py:161](../../backend/app/api/routes/companies.py) | `company_id: int` | `Depends(require_superadmin)` | `CompanyResponse` / `200` |
| `GET /api/dashboard/stats` | `get_dashboard_stats` — [backend/app/api/routes/dashboard.py:17](../../backend/app/api/routes/dashboard.py) | `—` | `Depends(get_current_user)` | `DashboardStats` / `200` |
| `GET /api/equipment/` | `get_equipment` — [backend/app/api/routes/equipment.py:15](../../backend/app/api/routes/equipment.py) | `cliente_id: Optional[int] = None` | `Depends(check_permission('equipos', 'ver'))` | `List[EquipmentResponse]` / `200` |
| `POST /api/equipment/` | `create_equipment` — [backend/app/api/routes/equipment.py:29](../../backend/app/api/routes/equipment.py) | `eq_in: EquipmentCreate` | `Depends(check_permission('equipos', 'crear'))` | `EquipmentResponse` / `status.HTTP_201_CREATED` |
| `GET /api/invoices/` | `list_invoices` — [backend/app/api/routes/invoices.py:100](../../backend/app/api/routes/invoices.py) | `—` | `Depends(check_permission('comprobantes', 'ver'))` | `List[InvoiceListResponse]` / `200` |
| `GET /api/invoices/{invoice_id}` | `get_invoice` — [backend/app/api/routes/invoices.py:118](../../backend/app/api/routes/invoices.py) | `invoice_id: int` | `Depends(check_permission('comprobantes', 'ver'))` | `InvoiceResponse` / `200` |
| `POST /api/invoices/` | `create_invoice` — [backend/app/api/routes/invoices.py:147](../../backend/app/api/routes/invoices.py) | `invoice_in: InvoiceCreate` | `Depends(check_permission('comprobantes', 'crear'))` | `InvoiceResponse` / `status.HTTP_201_CREATED` |
| `PATCH /api/invoices/{invoice_id}/anular` | `cancel_invoice` — [backend/app/api/routes/invoices.py:301](../../backend/app/api/routes/invoices.py) | `invoice_id: int` | `Depends(check_permission('comprobantes', 'editar'))` | `InvoiceResponse` / `200` |
| `GET /api/invoices/{invoice_id}/pdf` | `generate_invoice_pdf` — [backend/app/api/routes/invoices.py:351](../../backend/app/api/routes/invoices.py) | `invoice_id: int` | `Depends(check_permission('comprobantes', 'ver'))` | `dict / respuesta directa` / `200` |
| `GET /api/licenses/` | `get_licenses` — [backend/app/api/routes/licenses.py:64](../../backend/app/api/routes/licenses.py) | `categoria: Optional[str] = None; cliente_id: Optional[int] = None` | `Depends(check_permission('licencias', 'ver'))` | `List[LicenseResponse]` / `200` |
| `POST /api/licenses/` | `create_license` — [backend/app/api/routes/licenses.py:83](../../backend/app/api/routes/licenses.py) | `lic_in: LicenseCreate` | `Depends(check_permission('licencias', 'crear'))` | `LicenseResponse` / `status.HTTP_201_CREATED` |
| `PUT /api/licenses/{license_id}` | `update_license` — [backend/app/api/routes/licenses.py:138](../../backend/app/api/routes/licenses.py) | `license_id: int; lic_in: LicenseUpdate` | `Depends(check_permission('licencias', 'editar'))` | `LicenseResponse` / `200` |
| `DELETE /api/licenses/{license_id}` | `delete_license` — [backend/app/api/routes/licenses.py:183](../../backend/app/api/routes/licenses.py) | `license_id: int` | `Depends(check_permission('licencias', 'eliminar'))` | `dict / respuesta directa` / `status.HTTP_204_NO_CONTENT` |
| `POST /api/notifications/send` | `send_notification` — [backend/app/api/routes/notifications.py:13](../../backend/app/api/routes/notifications.py) | `req: NotificationSendRequest` | `Depends(get_current_user)` | `NotificationResponse` / `200` |
| `GET /api/payments/` | `list_payments` — [backend/app/api/routes/payments.py:71](../../backend/app/api/routes/payments.py) | `—` | `Depends(check_permission('pagos', 'ver'))` | `List[PaymentResponse]` / `200` |
| `GET /api/payments/service/{servicio_id}` | `get_service_payments` — [backend/app/api/routes/payments.py:81](../../backend/app/api/routes/payments.py) | `servicio_id: int` | `Depends(check_permission('pagos', 'ver'))` | `PaymentListResponse` / `200` |
| `POST /api/payments/` | `register_payment` — [backend/app/api/routes/payments.py:123](../../backend/app/api/routes/payments.py) | `payment_in: PaymentCreate` | `Depends(check_permission('pagos', 'crear'))` | `PaymentResponse` / `status.HTTP_201_CREATED` |
| `PATCH /api/payments/{payment_id}/anular` | `cancel_payment` — [backend/app/api/routes/payments.py:198](../../backend/app/api/routes/payments.py) | `payment_id: int` | `Depends(check_permission('pagos', 'editar'))` | `PaymentResponse` / `200` |
| `GET /api/products/` | `get_products` — [backend/app/api/routes/products.py:14](../../backend/app/api/routes/products.py) | `—` | `Depends(check_permission('productos', 'ver'))` | `List[ProductResponse]` / `200` |
| `POST /api/products/` | `create_product` — [backend/app/api/routes/products.py:24](../../backend/app/api/routes/products.py) | `prod_in: ProductCreate` | `Depends(check_permission('productos', 'crear'))` | `ProductResponse` / `status.HTTP_201_CREATED` |
| `GET /api/services/` | `get_services` — [backend/app/api/routes/services.py:26](../../backend/app/api/routes/services.py) | `cliente_id: Optional[int] = None` | `Depends(check_permission('servicios', 'ver'))` | `List[ServiceResponse]` / `200` |
| `GET /api/services/{service_id}` | `get_service` — [backend/app/api/routes/services.py:41](../../backend/app/api/routes/services.py) | `service_id: int` | `Depends(check_permission('servicios', 'ver'))` | `ServiceResponse` / `200` |
| `POST /api/services/` | `create_service` — [backend/app/api/routes/services.py:61](../../backend/app/api/routes/services.py) | `service_in: ServiceCreate` | `Depends(check_permission('servicios', 'crear'))` | `ServiceResponse` / `status.HTTP_201_CREATED` |
| `PATCH /api/services/{service_id}/status` | `update_service_status` — [backend/app/api/routes/services.py:128](../../backend/app/api/routes/services.py) | `service_id: int; status_in: ServiceUpdateStatus` | `Depends(check_permission('servicios', 'editar'))` | `ServiceResponse` / `200` |
| `POST /api/services/{service_id}/products` | `add_product_to_service` — [backend/app/api/routes/services.py:176](../../backend/app/api/routes/services.py) | `service_id: int; prod_in: AddProductToService` | `Depends(check_permission('servicios', 'editar'))` | `dict / respuesta directa` / `200` |
| `POST /api/uploads/file` | `upload_file` — [backend/app/api/routes/uploads.py:25](../../backend/app/api/routes/uploads.py) | `file: UploadFile = File(...)` | `Público` | `dict / respuesta directa` / `200` |
| `POST /api/uploads/session/create` | `create_upload_session` — [backend/app/api/routes/uploads.py:53](../../backend/app/api/routes/uploads.py) | `—` | `Público` | `SessionResponse` / `200` |
| `GET /api/uploads/session/{session_id}` | `get_upload_session` — [backend/app/api/routes/uploads.py:70](../../backend/app/api/routes/uploads.py) | `session_id: str` | `Público` | `SessionResponse` / `200` |
| `POST /api/uploads/session/{session_id}/upload` | `upload_session_photo` — [backend/app/api/routes/uploads.py:83](../../backend/app/api/routes/uploads.py) | `session_id: str; file: UploadFile = File(...)` | `Público` | `dict / respuesta directa` / `200` |
| `GET /api/users/roles` | `get_roles` — [backend/app/api/routes/users.py:15](../../backend/app/api/routes/users.py) | `—` | `Depends(require_admin)` | `dict / respuesta directa` / `200` |
| `GET /api/users/` | `get_users` — [backend/app/api/routes/users.py:27](../../backend/app/api/routes/users.py) | `empresa_id: Optional[int] = None` | `Depends(require_admin)` | `List[UserResponse]` / `200` |
| `POST /api/users/` | `create_user` — [backend/app/api/routes/users.py:45](../../backend/app/api/routes/users.py) | `user_in: UserCreate` | `Depends(require_admin)` | `UserResponse` / `status.HTTP_201_CREATED` |
| `PUT /api/users/{user_id}` | `update_user` — [backend/app/api/routes/users.py:101](../../backend/app/api/routes/users.py) | `user_id: int; user_in: UserUpdate` | `Depends(require_admin)` | `UserResponse` / `200` |

## Cuerpos y respuestas: campos completos

Los campos heredados también se enumeran. `sin default` significa requerido por el schema, incluso si su tipo permite null. `Field(...)` conserva restricciones declaradas. Este inventario describe las clases, incluidas las no conectadas; no implica que todas tengan endpoint. Validadores de LicenseCreate se explican en F12. Config de respuestas usa from_attributes.

Los siguientes contratos existen sin ruta de escritura correspondiente: ProductUpdate, InventoryMovementCreate, ServiceItemCreate, InvoiceItemCreate y CompanyCreate (alta real usa CompanyWithAdminCreate). Ver imports y firmas de routers de la tabla anterior.

### `AuditResponse`

[backend/app/schemas/audit.py:5](../../backend/app/schemas/audit.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `usuario_id` | `Optional[int]` | `None` |
| `accion` | `str` | `sin default` |
| `entidad` | `str` | `sin default` |
| `entidad_id` | `Optional[int]` | `None` |
| `descripcion` | `str` | `sin default` |
| `fecha` | `datetime` | `sin default` |

### `Token`

[backend/app/schemas/auth.py:4](../../backend/app/schemas/auth.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `access_token` | `str` | `sin default` |
| `token_type` | `str` | `sin default` |
| `user_id` | `int` | `sin default` |
| `nombre` | `str` | `sin default` |
| `email` | `str` | `sin default` |
| `rol` | `str` | `sin default` |
| `empresa_id` | `Optional[int]` | `None` |
| `empresa_nombre` | `Optional[str]` | `None` |
| `permisos` | `Optional[Dict[str, Any]]` | `None` |

### `LoginRequest`

[backend/app/schemas/auth.py:15](../../backend/app/schemas/auth.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `email` | `EmailStr` | `sin default` |
| `password` | `str` | `sin default` |

### `ClientBase`

[backend/app/schemas/client.py:5](../../backend/app/schemas/client.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombres` | `str` | `sin default` |
| `apellidos` | `str` | `sin default` |
| `documento` | `str` | `sin default` |
| `telefono` | `str` | `sin default` |
| `email` | `Optional[EmailStr]` | `None` |
| `direccion` | `Optional[str]` | `None` |

### `ClientCreate`

[backend/app/schemas/client.py:13](../../backend/app/schemas/client.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombres` | `str` | `sin default` |
| `apellidos` | `str` | `sin default` |
| `documento` | `str` | `sin default` |
| `telefono` | `str` | `sin default` |
| `email` | `Optional[EmailStr]` | `None` |
| `direccion` | `Optional[str]` | `None` |

### `ClientUpdate`

[backend/app/schemas/client.py:16](../../backend/app/schemas/client.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombres` | `Optional[str]` | `None` |
| `apellidos` | `Optional[str]` | `None` |
| `documento` | `Optional[str]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `email` | `Optional[EmailStr]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `activo` | `Optional[bool]` | `None` |

### `ClientResponse`

[backend/app/schemas/client.py:25](../../backend/app/schemas/client.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombres` | `str` | `sin default` |
| `apellidos` | `str` | `sin default` |
| `documento` | `str` | `sin default` |
| `telefono` | `str` | `sin default` |
| `email` | `Optional[EmailStr]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `id` | `int` | `sin default` |
| `activo` | `bool` | `sin default` |
| `created_at` | `datetime` | `sin default` |

### `CompanyBase`

[backend/app/schemas/company.py:5](../../backend/app/schemas/company.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `ruc_documento` | `Optional[str]` | `None` |
| `email_contacto` | `Optional[EmailStr]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `limite_usuarios` | `int` | `10` |
| `modulos_permitidos` | `Optional[Dict[str, Any]]` | `None` |

### `CompanyCreate`

[backend/app/schemas/company.py:14](../../backend/app/schemas/company.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `ruc_documento` | `Optional[str]` | `None` |
| `email_contacto` | `Optional[EmailStr]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `limite_usuarios` | `int` | `10` |
| `modulos_permitidos` | `Optional[Dict[str, Any]]` | `None` |

### `CompanyUpdate`

[backend/app/schemas/company.py:17](../../backend/app/schemas/company.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `Optional[str]` | `None` |
| `ruc_documento` | `Optional[str]` | `None` |
| `email_contacto` | `Optional[EmailStr]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `activo` | `Optional[bool]` | `None` |
| `limite_usuarios` | `Optional[int]` | `None` |
| `modulos_permitidos` | `Optional[Dict[str, Any]]` | `None` |

### `CompanyResponse`

[backend/app/schemas/company.py:27](../../backend/app/schemas/company.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `ruc_documento` | `Optional[str]` | `None` |
| `email_contacto` | `Optional[EmailStr]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `limite_usuarios` | `int` | `10` |
| `modulos_permitidos` | `Optional[Dict[str, Any]]` | `None` |
| `id` | `int` | `sin default` |
| `activo` | `bool` | `sin default` |
| `total_usuarios` | `Optional[int]` | `0` |
| `created_at` | `datetime` | `sin default` |
| `updated_at` | `datetime` | `sin default` |

### `CompanyWithAdminCreate`

[backend/app/schemas/company.py:37](../../backend/app/schemas/company.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `ruc_documento` | `Optional[str]` | `None` |
| `email_contacto` | `Optional[EmailStr]` | `None` |
| `telefono` | `Optional[str]` | `None` |
| `direccion` | `Optional[str]` | `None` |
| `limite_usuarios` | `int` | `10` |
| `admin_nombre` | `str` | `sin default` |
| `admin_email` | `EmailStr` | `sin default` |
| `admin_password` | `str` | `sin default` |

### `DashboardStats`

[backend/app/schemas/dashboard.py:3](../../backend/app/schemas/dashboard.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `total_clientes` | `int` | `sin default` |
| `servicios_pendientes` | `int` | `sin default` |
| `servicios_en_proceso` | `int` | `sin default` |
| `servicios_terminados` | `int` | `sin default` |
| `productos_stock_bajo` | `int` | `sin default` |
| `ingresos_hoy` | `float` | `sin default` |

### `EquipmentBase`

[backend/app/schemas/equipment.py:5](../../backend/app/schemas/equipment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `tipo` | `str` | `sin default` |
| `marca` | `str` | `sin default` |
| `modelo` | `str` | `sin default` |
| `numero_serie` | `Optional[str]` | `None` |
| `descripcion` | `Optional[str]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |

### `EquipmentCreate`

[backend/app/schemas/equipment.py:14](../../backend/app/schemas/equipment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `tipo` | `str` | `sin default` |
| `marca` | `str` | `sin default` |
| `modelo` | `str` | `sin default` |
| `numero_serie` | `Optional[str]` | `None` |
| `descripcion` | `Optional[str]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |

### `EquipmentResponse`

[backend/app/schemas/equipment.py:17](../../backend/app/schemas/equipment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `tipo` | `str` | `sin default` |
| `marca` | `str` | `sin default` |
| `modelo` | `str` | `sin default` |
| `numero_serie` | `Optional[str]` | `None` |
| `descripcion` | `Optional[str]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |
| `id` | `int` | `sin default` |
| `created_at` | `datetime` | `sin default` |

### `InventoryMovementCreate`

[backend/app/schemas/inventory.py:6](../../backend/app/schemas/inventory.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `producto_id` | `int` | `sin default` |
| `tipo` | `MovementType` | `sin default` |
| `cantidad` | `int` | `sin default` |
| `observacion` | `Optional[str]` | `None` |

### `InventoryMovementResponse`

[backend/app/schemas/inventory.py:12](../../backend/app/schemas/inventory.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `producto_id` | `int` | `sin default` |
| `tipo` | `MovementType` | `sin default` |
| `cantidad` | `int` | `sin default` |
| `servicio_id` | `Optional[int]` | `None` |
| `usuario_id` | `int` | `sin default` |
| `fecha` | `datetime` | `sin default` |
| `observacion` | `Optional[str]` | `None` |

### `InvoiceItemCreate`

[backend/app/schemas/invoice.py:10](../../backend/app/schemas/invoice.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `producto_id` | `Optional[int]` | `None` |
| `concepto` | `str` | `Field(min_length=1, max_length=255)` |
| `cantidad` | `Decimal` | `Field(gt=0)` |
| `precio_unitario` | `Decimal` | `Field(ge=0)` |

### `InvoiceItemResponse`

[backend/app/schemas/invoice.py:17](../../backend/app/schemas/invoice.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `comprobante_id` | `int` | `sin default` |
| `producto_id` | `Optional[int]` | `None` |
| `concepto` | `str` | `sin default` |
| `cantidad` | `Decimal` | `sin default` |
| `precio_unitario` | `Decimal` | `sin default` |
| `subtotal` | `Decimal` | `sin default` |

### `InvoiceCreate`

[backend/app/schemas/invoice.py:29](../../backend/app/schemas/invoice.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `servicio_id` | `int` | `sin default` |
| `tipo_comprobante` | `InvoiceType` | `sin default` |
| `serie` | `str` | `Field(min_length=1, max_length=10)` |
| `observaciones` | `Optional[str]` | `None` |

### `InvoiceResponse`

[backend/app/schemas/invoice.py:36](../../backend/app/schemas/invoice.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `servicio_id` | `int` | `sin default` |
| `cliente_id` | `int` | `sin default` |
| `usuario_id` | `int` | `sin default` |
| `tipo_comprobante` | `InvoiceType` | `sin default` |
| `serie` | `str` | `sin default` |
| `numero` | `int` | `sin default` |
| `fecha_emision` | `datetime` | `sin default` |
| `cliente_nombre` | `str` | `sin default` |
| `cliente_documento` | `str` | `sin default` |
| `cliente_direccion` | `Optional[str]` | `None` |
| `subtotal` | `Decimal` | `sin default` |
| `total` | `Decimal` | `sin default` |
| `estado` | `InvoiceStatus` | `sin default` |
| `observaciones` | `Optional[str]` | `None` |
| `created_at` | `datetime` | `sin default` |
| `detalles` | `List[InvoiceItemResponse]` | `[]` |

### `InvoiceListResponse`

[backend/app/schemas/invoice.py:58](../../backend/app/schemas/invoice.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `servicio_id` | `int` | `sin default` |
| `cliente_id` | `int` | `sin default` |
| `tipo_comprobante` | `InvoiceType` | `sin default` |
| `serie` | `str` | `sin default` |
| `numero` | `int` | `sin default` |
| `fecha_emision` | `datetime` | `sin default` |
| `cliente_nombre` | `str` | `sin default` |
| `cliente_documento` | `str` | `sin default` |
| `subtotal` | `Decimal` | `sin default` |
| `total` | `Decimal` | `sin default` |
| `estado` | `InvoiceStatus` | `sin default` |

### `LicenseBase`

[backend/app/schemas/license.py:5](../../backend/app/schemas/license.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `Optional[int]` | `None` |
| `equipo_id` | `Optional[int]` | `None` |
| `categoria` | `str` | `'ANTIVIRUS'` |
| `nombre_producto` | `str` | `sin default` |
| `clave_licencia` | `str` | `sin default` |
| `cantidad_dispositivos` | `int` | `1` |
| `es_permanente` | `bool` | `False` |
| `fecha_inicio` | `Optional[date]` | `None` |
| `fecha_fin` | `Optional[date]` | `None` |
| `proveedor` | `Optional[str]` | `None` |
| `notas` | `Optional[str]` | `None` |

### `LicenseCreate`

[backend/app/schemas/license.py:18](../../backend/app/schemas/license.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `Optional[int]` | `None` |
| `equipo_id` | `Optional[int]` | `None` |
| `categoria` | `str` | `'ANTIVIRUS'` |
| `nombre_producto` | `str` | `sin default` |
| `clave_licencia` | `str` | `sin default` |
| `cantidad_dispositivos` | `int` | `1` |
| `es_permanente` | `bool` | `False` |
| `fecha_inicio` | `Optional[date]` | `None` |
| `fecha_fin` | `Optional[date]` | `None` |
| `proveedor` | `Optional[str]` | `None` |
| `notas` | `Optional[str]` | `None` |

### `LicenseUpdate`

[backend/app/schemas/license.py:34](../../backend/app/schemas/license.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `Optional[int]` | `None` |
| `equipo_id` | `Optional[int]` | `None` |
| `categoria` | `Optional[str]` | `None` |
| `nombre_producto` | `Optional[str]` | `None` |
| `clave_licencia` | `Optional[str]` | `None` |
| `cantidad_dispositivos` | `Optional[int]` | `None` |
| `es_permanente` | `Optional[bool]` | `None` |
| `fecha_inicio` | `Optional[date]` | `None` |
| `fecha_fin` | `Optional[date]` | `None` |
| `proveedor` | `Optional[str]` | `None` |
| `notas` | `Optional[str]` | `None` |

### `LicenseResponse`

[backend/app/schemas/license.py:47](../../backend/app/schemas/license.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `Optional[int]` | `None` |
| `equipo_id` | `Optional[int]` | `None` |
| `categoria` | `str` | `'ANTIVIRUS'` |
| `nombre_producto` | `str` | `sin default` |
| `clave_licencia` | `str` | `sin default` |
| `cantidad_dispositivos` | `int` | `1` |
| `es_permanente` | `bool` | `False` |
| `fecha_inicio` | `Optional[date]` | `None` |
| `fecha_fin` | `Optional[date]` | `None` |
| `proveedor` | `Optional[str]` | `None` |
| `notas` | `Optional[str]` | `None` |
| `id` | `int` | `sin default` |
| `empresa_id` | `int` | `sin default` |
| `cliente_nombre` | `Optional[str]` | `None` |
| `equipo_info` | `Optional[str]` | `None` |
| `dias_restantes` | `Optional[int]` | `None` |
| `estado_vencimiento` | `str` | `'ACTIVA'` |
| `created_at` | `datetime` | `sin default` |
| `updated_at` | `datetime` | `sin default` |

### `NotificationSendRequest`

[backend/app/schemas/notification.py:4](../../backend/app/schemas/notification.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `servicio_id` | `int` | `sin default` |
| `mensaje` | `str` | `sin default` |

### `NotificationResponse`

[backend/app/schemas/notification.py:8](../../backend/app/schemas/notification.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `cliente_id` | `int` | `sin default` |
| `servicio_id` | `int` | `sin default` |
| `tipo` | `str` | `sin default` |
| `mensaje` | `str` | `sin default` |
| `estado` | `str` | `sin default` |
| `fecha` | `datetime` | `sin default` |

### `PaymentCreate`

[backend/app/schemas/payment.py:8](../../backend/app/schemas/payment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `servicio_id` | `int` | `sin default` |
| `monto` | `float` | `Field(gt=0)` |
| `metodo_pago` | `PaymentMethod` | `sin default` |

### `PaymentResponse`

[backend/app/schemas/payment.py:14](../../backend/app/schemas/payment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `servicio_id` | `int` | `sin default` |
| `monto` | `float` | `sin default` |
| `metodo_pago` | `PaymentMethod` | `sin default` |
| `estado` | `PaymentStatus` | `sin default` |
| `fecha` | `datetime` | `sin default` |
| `usuario_id` | `int` | `sin default` |

### `PaymentFinancialSummary`

[backend/app/schemas/payment.py:26](../../backend/app/schemas/payment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `servicio_id` | `int` | `sin default` |
| `mano_de_obra` | `float` | `sin default` |
| `total_productos` | `float` | `sin default` |
| `total_servicio` | `float` | `sin default` |
| `total_pagado` | `float` | `sin default` |
| `saldo_pendiente` | `float` | `sin default` |
| `estado_financiero` | `str` | `sin default` |

### `PaymentListResponse`

[backend/app/schemas/payment.py:36](../../backend/app/schemas/payment.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `pagos` | `list[PaymentResponse]` | `sin default` |
| `resumen` | `PaymentFinancialSummary` | `sin default` |

### `ProductBase`

[backend/app/schemas/product.py:5](../../backend/app/schemas/product.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `categoria` | `str` | `sin default` |
| `codigo` | `str` | `sin default` |
| `stock` | `int` | `sin default` |
| `stock_minimo` | `int` | `2` |
| `precio_compra` | `float` | `sin default` |
| `precio_venta` | `float` | `sin default` |

### `ProductCreate`

[backend/app/schemas/product.py:14](../../backend/app/schemas/product.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `categoria` | `str` | `sin default` |
| `codigo` | `str` | `sin default` |
| `stock` | `int` | `sin default` |
| `stock_minimo` | `int` | `2` |
| `precio_compra` | `float` | `sin default` |
| `precio_venta` | `float` | `sin default` |

### `ProductUpdate`

[backend/app/schemas/product.py:17](../../backend/app/schemas/product.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `Optional[str]` | `None` |
| `categoria` | `Optional[str]` | `None` |
| `codigo` | `Optional[str]` | `None` |
| `stock` | `Optional[int]` | `None` |
| `stock_minimo` | `Optional[int]` | `None` |
| `precio_compra` | `Optional[float]` | `None` |
| `precio_venta` | `Optional[float]` | `None` |
| `activo` | `Optional[bool]` | `None` |

### `ProductResponse`

[backend/app/schemas/product.py:27](../../backend/app/schemas/product.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `categoria` | `str` | `sin default` |
| `codigo` | `str` | `sin default` |
| `stock` | `int` | `sin default` |
| `stock_minimo` | `int` | `2` |
| `precio_compra` | `float` | `sin default` |
| `precio_venta` | `float` | `sin default` |
| `id` | `int` | `sin default` |
| `activo` | `bool` | `sin default` |
| `created_at` | `datetime` | `sin default` |

### `ServiceBase`

[backend/app/schemas/service.py:10](../../backend/app/schemas/service.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `equipo_id` | `Optional[int]` | `None` |
| `tipo_servicio` | `str` | `sin default` |
| `descripcion` | `str` | `sin default` |
| `fecha_estimada` | `Optional[datetime]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |

### `ServiceCreate`

[backend/app/schemas/service.py:19](../../backend/app/schemas/service.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `equipo_id` | `Optional[int]` | `None` |
| `tipo_servicio` | `str` | `sin default` |
| `descripcion` | `str` | `sin default` |
| `fecha_estimada` | `Optional[datetime]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |
| `usuario_responsable_id` | `Optional[int]` | `None` |
| `monto` | `Optional[float]` | `0.0` |

### `ServiceUpdateStatus`

[backend/app/schemas/service.py:24](../../backend/app/schemas/service.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `estado` | `ServiceStatus` | `sin default` |
| `diagnostico` | `Optional[str]` | `None` |
| `monto` | `Optional[float]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |

### `AddProductToService`

[backend/app/schemas/service.py:31](../../backend/app/schemas/service.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `producto_id` | `int` | `sin default` |
| `cantidad` | `int` | `sin default` |

### `ServiceResponse`

[backend/app/schemas/service.py:36](../../backend/app/schemas/service.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `cliente_id` | `int` | `sin default` |
| `equipo_id` | `Optional[int]` | `None` |
| `tipo_servicio` | `str` | `sin default` |
| `descripcion` | `str` | `sin default` |
| `fecha_estimada` | `Optional[datetime]` | `None` |
| `imagen_url` | `Optional[str]` | `None` |
| `id` | `int` | `sin default` |
| `usuario_responsable_id` | `Optional[int]` | `None` |
| `diagnostico` | `Optional[str]` | `None` |
| `estado` | `ServiceStatus` | `sin default` |
| `monto` | `float` | `sin default` |
| `fecha_ingreso` | `datetime` | `sin default` |
| `fecha_finalizacion` | `Optional[datetime]` | `None` |
| `created_at` | `datetime` | `sin default` |
| `items` | `List[ServiceItemResponse]` | `[]` |

### `ServiceItemCreate`

[backend/app/schemas/service_item.py:5](../../backend/app/schemas/service_item.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `producto_id` | `int` | `sin default` |
| `cantidad` | `int` | `sin default` |

### `ServiceItemResponse`

[backend/app/schemas/service_item.py:10](../../backend/app/schemas/service_item.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `servicio_id` | `int` | `sin default` |
| `producto_id` | `int` | `sin default` |
| `cantidad` | `int` | `sin default` |
| `precio_unitario` | `float` | `sin default` |
| `subtotal` | `float` | `sin default` |
| `created_at` | `datetime` | `sin default` |

### `RoleSchema`

[backend/app/schemas/user.py:5](../../backend/app/schemas/user.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `id` | `int` | `sin default` |
| `nombre` | `str` | `sin default` |

### `UserBase`

[backend/app/schemas/user.py:10](../../backend/app/schemas/user.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `email` | `EmailStr` | `sin default` |
| `rol_id` | `int` | `sin default` |
| `permisos` | `Optional[Dict[str, Any]]` | `None` |

### `UserCreate`

[backend/app/schemas/user.py:16](../../backend/app/schemas/user.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `email` | `EmailStr` | `sin default` |
| `rol_id` | `int` | `sin default` |
| `permisos` | `Optional[Dict[str, Any]]` | `None` |
| `password` | `str` | `sin default` |
| `empresa_id` | `Optional[int]` | `None` |

### `UserUpdate`

[backend/app/schemas/user.py:20](../../backend/app/schemas/user.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `Optional[str]` | `None` |
| `email` | `Optional[EmailStr]` | `None` |
| `rol_id` | `Optional[int]` | `None` |
| `password` | `Optional[str]` | `None` |
| `activo` | `Optional[bool]` | `None` |
| `permisos` | `Optional[Dict[str, Any]]` | `None` |

### `UserResponse`

[backend/app/schemas/user.py:28](../../backend/app/schemas/user.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `nombre` | `str` | `sin default` |
| `email` | `EmailStr` | `sin default` |
| `rol_id` | `int` | `sin default` |
| `permisos` | `Optional[Dict[str, Any]]` | `None` |
| `id` | `int` | `sin default` |
| `empresa_id` | `Optional[int]` | `None` |
| `activo` | `bool` | `sin default` |
| `rol` | `RoleSchema` | `sin default` |
| `created_at` | `datetime` | `sin default` |

### `SessionResponse`

[backend/app/api/routes/uploads.py:18](../../backend/app/api/routes/uploads.py)

| Campo | Tipo | Default / restricción |
|---|---|---|
| `session_id` | `str` | `sin default` |
| `status` | `str` | `sin default` |
| `photo_url` | `Optional[str]` | `None` |
| `created_at` | `str` | `sin default` |

## Respuestas directas y endpoints auxiliares

### Errores y particularidades de contrato

Los HTTPException declarados incluyen `detail` de texto: 400 para reglas de negocio, 401 para credenciales/token y 403 para autorización/empresa, 404 para recursos inexistentes o fuera de ámbito. La validación de cuerpo usa los schemas Pydantic y puede producir 422 con `detail` estructurado; no todos los componentes React convierten esa lista a texto. Los errores inesperados de BD no tienen contrato propio definido. Referencias: `backend/app/api/deps.py:12-74`, `backend/app/api/routes/payments.py:134-169`, `frontend/src/pages/Equipment.jsx:82-104`, `frontend/src/pages/Licenses.jsx:181-183`.

`OAuth2PasswordBearer` declara tokenUrl, pero el handler login exige LoginRequest JSON, no formulario OAuth2PasswordRequestForm. Por tanto, no debe asumirse compatibilidad de un cliente OAuth2 que envíe `username/password` form solo por el esquema de seguridad. Login devuelve rol string; `/auth/me` devuelve RoleSchema anidado y no incluye empresa_nombre. Fuentes: `backend/app/api/deps.py:10`, `backend/app/api/routes/auth.py:13-56`, `backend/app/schemas/auth.py:4-17`, `backend/app/schemas/user.py:28-34`.

Los PUT implementados son actualizaciones parciales mediante `model_dump(exclude_unset=True)`: omitir un campo conserva su valor; enviarlo explícitamente null lo asigna, salvo tratamiento particular de password. No hay normalización uniforme de textos: UI recorta muchos campos, API generalmente conserva lo recibido, excepto categoría de licencia y serie de comprobante. Referencias: `backend/app/api/routes/users.py:115-122`, `clients.py:68-69`, `companies.py:126-128`, `licenses.py:152-157`, `invoices.py:214`.

- POST `/services/{id}/products`: `{message, service_item:{id,servicio_id,producto_id,cantidad,precio_unitario,subtotal,created_at}, stock_actual}` (`backend/app/api/routes/services.py:260-272`).
- GET `/users/roles`: array `{id,nombre}` (`backend/app/api/routes/users.py:14-24`).
- POST `/uploads/file`: `{url,filename}`; POST `/uploads/session/{id}/upload`: `{status:"COMPLETED",photo_url}` (`backend/app/api/routes/uploads.py:49-50,114-118`).
- DELETE `/licenses/{id}`: 204, sin cuerpo (`backend/app/api/routes/licenses.py:182-207`).
- GET `/invoices/{id}/pdf`: StreamingResponse application/pdf y Content-Disposition attachment (`backend/app/api/routes/invoices.py:1481-1494`).
- FastAPI configura OpenAPI en `/api/openapi.json`; conserva páginas documentales por defecto. `/static` sirve archivos por StaticFiles. No hay health endpoint propio en main (`backend/app/main.py:26-54`).

## Contraste del OpenAPI guardado

El archivo raíz `openapi.json` es una instantánea (título SisTec API, versión 0.1.0), no se importa desde la aplicación. Las diferencias siguientes se obtuvieron comparando todas sus operaciones con decoradores de routers montados.

Operaciones en snapshot: 27; actuales: 42. Ausentes en snapshot:
- `DELETE /api/licenses/{license_id}`
- `GET /api/companies/`
- `GET /api/invoices/{invoice_id}/pdf`
- `GET /api/licenses/`
- `GET /api/uploads/session/{session_id}`
- `GET /api/users/roles`
- `PATCH /api/companies/{company_id}/toggle-status`
- `POST /api/companies/`
- `POST /api/licenses/`
- `POST /api/uploads/file`
- `POST /api/uploads/session/create`
- `POST /api/uploads/session/{session_id}/upload`
- `PUT /api/companies/{company_id}`
- `PUT /api/licenses/{license_id}`
- `PUT /api/users/{user_id}`

También faltan campos recientes: la comparación campo por campo queda en `contraste-openapi.json`. Los esquemas actuales de esta documentación derivan del código, sin regenerar ni sustituir el OpenAPI original.

## Integraciones externas y fronteras

| Integración | Información transmitida / comportamiento | Evidencia |
|---|---|---|
| PostgreSQL | Datos de negocio vía SQLAlchemy/psycopg2; conexión interna de Compose | `backend/app/db/session.py:5-14`; `docker-compose.yml:32` |
| api.qrserver.com | GET de imagen con URL completa de captura e ID de sesión en query data | `frontend/src/components/ImageUploadControl.jsx:105-106` |
| images.unsplash.com | Descarga de tres fondos de login desde navegador | `frontend/src/pages/Login.jsx:33-53` |
| via.placeholder.com | Imagen sustitutiva si falla foto de formulario | `frontend/src/components/ImageUploadControl.jsx:145-147` |
| APIs navegador | localStorage, clipboard, FileReader, Blob/ObjectURL, file capture | AuthContext, Licenses, MobileCameraUpload, Invoices |

No se encontraron clientes SMTP/SMS/WhatsApp, SUNAT, pasarela de pago, almacenamiento de objetos ni servicio de suscripciones en los imports, manifiestos y recorridos inspeccionados. «ENVIADO» y métodos de pago no prueban entrega o cobro externo. Fuente: `backend/app/services/notification_service.py:5-26`, `backend/app/api/routes/payments.py:172-195`, `backend/app/api/routes/invoices.py:1465-1469`, [dependencias](08-dependencias.md). No se contactaron estos servicios durante el análisis.
