El SSO estandar Odoo no funciona con Azure AD

Hay que poner el repositorio de este módulo delante de los addons Odoo (como se hace habitualmente). Con ello conseguimos que Odoo cargue nuestra funcionalidad en lugar de la estándar.

Configuración
================

Solicitar la creación de una aplicación en Azure AD SIN las marcas de "Tokens de acceso de usuario" ni "Tokens de ID" en la sección "Flujos de concesión e híbridos".

1. Entrar en Odoo en modo desarrollador (Activar el modo desarrollador en la URL añadiendo `?debug=1`).
2. Ir a Ajustes > Usuarios y Compañías > Proveedores de OAuth
3. Crear un nuevo proveedor de OAuth con los siguientes datos:
   - Nombre: Azure
   - Id. de cliente: (ID de la aplicación creada en Azure AD)
   - Contenido: Azure (es el código para el botón de inicio de sesión)
   - URL de autorización: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize
   - Ámbito: openid profile email
   - URL de validación: https://graph.microsoft.com/oidc/userinfo