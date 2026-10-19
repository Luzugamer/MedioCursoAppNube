# Despliegue de multitenancy con tablas compartidas

La revisión `0006` agrega pertenencia a empresa en los detalles y restricciones entre módulos. El arranque de la nueva imagen ejecuta `alembic upgrade head`; **no** aplica la migración a la base de datos del equipo hasta reconstruir y arrancar el backend. El proceso se verificó en instancias temporales PostgreSQL 16, tanto con una base nueva como con un esquema previo poblado.

1. Detener las escrituras del backend y hacer una copia `pg_dump -Fc` de la BD existente. Verificar que la copia se pueda restaurar en otra base.
2. Ejecutar `tenant_diagnostics.sql` contra una copia restaurada. Investigar cada fila devuelta y corregir la fuente del dato; no reasignar empresas por deducción. Repetir hasta obtener cero filas.
3. En esa copia, reconstruir la imagen del backend y arrancarla con `SEED_DEMO_DATA=false`, una `SECRET_KEY` propia y, si aún no existe un superadministrador, `BOOTSTRAP_SUPERADMIN_EMAIL` y `BOOTSTRAP_SUPERADMIN_PASSWORD`. Confirmar que `alembic_version` queda en `0006` y que la API funciona.
4. Ejecutar las pruebas de integración con dos empresas y verificar las descargas PDF, las restricciones SQL y la captura QR. Hacer el mismo procedimiento durante una ventana de mantenimiento en la BD de destino. Conservar la copia hasta completar la verificación.

Las fotos siguen siendo públicas por URL. Las nuevas se guardan bajo `/static/uploads/<empresa_id>/`; las URLs antiguas conservan su ruta. El enlace de captura QR es temporal y de un solo uso. El QR se dibuja en el navegador para no revelar ese enlace a un generador externo.

Para desarrollo, `SEED_DEMO_DATA=true` conserva los datos y cuentas de ejemplo. No usarlo en producción. Las instalaciones existentes con cuentas de ejemplo deben desactivarlas o cambiar sus contraseñas antes de exponer el servicio.
