# sdi_account_payment_return

## Instalación

1. Copia la carpeta `sdi_account_payment_return` en tu directorio de addons.
2. Actualiza la lista de aplicaciones en Odoo.
3. Instala el módulo desde el panel de aplicaciones.

## Configuración

1. Ve a **Ajustes Técnicos → Parámetros del sistema**.
2. Crea o edita el parámetro:
   - **Clave:** `sdi_account_payment_return.payment_return_mail_template_id`
   - **Valor:** ID de la plantilla de correo a usar (puedes obtenerlo desde la vista de plantillas de correo).

Si el parámetro no está definido o está vacío, el módulo usará la plantilla por defecto con el ID externo `sdi_account_payment_return.default_payment_return_email_template`.

## Uso

- Al registrar una devolución de pago, el sistema enviará un correo usando la plantilla configurada.
- El historial de correos enviados se adjuntará como nota en el registro de devolución.

## Notas

- Asegúrate de que la plantilla de correo tenga el destinatario configurado correctamente.
- Si necesitas personalizar la plantilla, edítala desde **Ajustes → Plantillas de correo**.
