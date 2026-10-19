# Ingeniería inversa de SisTec

Fecha de inspección: 13 de octubre de 2026. Alcance: copia local del proyecto, análisis estático del código propio, contratos, manifiestos, migraciones y configuración. No se ejecutó la aplicación ni se consultó una base de datos. No se leyeron `.env*`, dependencias instaladas ni el contenido de las fotografías. No se modificó código de la aplicación.

## Propósito y comportamiento real

SisTec permite a empresas registrar clientes, equipos y órdenes de servicio; asociar productos consumidos a una orden, cobrar importes parciales, emitir comprobantes internos y gestionar claves de software. Un usuario SUPERADMIN administra empresas y sus administradores. Los roles ADMIN, TECNICO y VENDEDOR operan mediante permisos por módulo. La implementación se encuentra en los routers registrados en `backend/app/main.py:41-54` y en las pantallas conectadas desde `frontend/src/App.jsx:85-348`.

El sistema emplea una SPA React, una API HTTP FastAPI y una base PostgreSQL compartida entre empresas. El aislamiento se implementa mediante filtros `empresa_id` en las consultas; no se encontró una política central de aislamiento a nivel de base de datos. La clasificación como monolito modular con cliente separado es una **inferencia arquitectónica**, sustentada por el único objeto FastAPI, una sesión SQLAlchemy común y tres servicios Compose. Véase [arquitectura](02-arquitectura.md).

## Alcance funcional comprobado en código

| Área | Resultado real |
|---|---|
| Identidad | Login JSON, JWT, bcrypt, sesión local del navegador, controles de usuario y empresa activos. |
| Empresas y usuarios | Alta de empresa con administrador, consulta y suspensión; usuarios con roles, permisos, contraseña y cupo por empresa. |
| Clientes y equipos | Clientes: alta, listado y edición; equipos: alta y listado. Las órdenes pueden carecer de equipo. |
| Servicios | Alta, consulta, diagnóstico y cambio de estado; consumo de productos con movimiento de salida y detalle valorizado. |
| Productos | Catálogo y stock inicial. No existe una API general de entradas, ajustes o historial de inventario. |
| Pagos | Registro manual, saldo por servicio y anulación. Yape/Plin son etiquetas de método; no hay conexión con pasarelas. |
| Comprobantes | Emisión desde una orden, consulta, anulación y PDF. No hay envío ni validación SUNAT. |
| Licencias | Registro de claves, asociación opcional con cliente/equipo, edición, eliminación y cálculo de vencimiento. No son suscripciones SaaS. |
| Fotos | Subida multipart y enlace móvil por QR; consulta periódica del estado y archivo local. |
| Seguimiento | Estadísticas y registros de auditoría en backend; pantalla de auditoría con datos estáticos. Notificaciones guardadas, sin entrega externa. |

La trazabilidad individual y los recorridos completos están en [catálogo](03-catalogo-funcionalidades.md), [API](06-apis-integraciones.md) y [flujos](07-flujos-ejecucion.md).

## Lectura prioritaria de hallazgos

El análisis identifica omisiones de aislamiento en el PDF de comprobantes, asignación de roles sin restricción del rol destino, actualización de relaciones de licencias sin comprobar empresa y diferencias entre permisos visuales y del servidor. También identifica migraciones históricas incompletas y arranque basado en `create_all` seguido de `stamp head`. Son observaciones del código; sus consecuencias en una instalación concreta no se probaron. Evidencias y condiciones en [hallazgos](10-hallazgos-incertidumbres.md).

## Índice

1. [Estructura del proyecto](01-estructura-proyecto.md)
2. [Arquitectura](02-arquitectura.md)
3. [Catálogo de funcionalidades](03-catalogo-funcionalidades.md)
4. [Reglas de negocio](04-reglas-negocio.md)
5. [Modelo y diccionario de datos](05-modelo-datos.md)
6. [API y contratos](06-apis-integraciones.md)
7. [Flujos de ejecución](07-flujos-ejecucion.md)
8. [Dependencias](08-dependencias.md)
9. [Configuración y despliegue](09-configuracion-despliegue.md)
10. [Hallazgos e incertidumbres](10-hallazgos-incertidumbres.md)
11. [Trazabilidad, cobertura y verificación](trazabilidad.md)

**Convención:** confirmado = visible en implementación; inferido = consecuencia razonada y condicionada; desconocido = requiere información o ejecución ajena al alcance. «Verificado» en el inventario significa contrastado estáticamente, no certificado en producción. Los números de línea corresponden a las huellas conservadas en `inventario.json`.
