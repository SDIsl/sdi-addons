# -*- coding: utf-8 -*-
{
    "name": "VeriFactu POS- Integración con la AEAT (España)",
    "version": "2.2.3",
    "author": "Mr Rubik",
    "maintainer": "Mr Rubik",
    "website": "https://www.mrrubik.com",
    "price": 399,
    "currency": "USD",
    "category": "Accounting",
    "summary": "Envío automático de facturas electrónicas a la AEAT con firma digital y código QR (VeriFactu).",
    "description": """
Este módulo implementa la integración completa con el sistema VeriFactu de la Agencia Tributaria Española, conforme al Real Decreto 1007/2023.

🔐 Firma digitalmente las facturas emitidas con certificados FNMT o PFX.
📤 Genera y envía automáticamente el XML estructurado a la AEAT.
🔗 Calcula y adjunta el hash y el código QR verificable conforme al esquema SUMI.
📑 Registra el estado del envío, errores de validación y reintentos automáticos.
🧾 Compatible tanto con facturación tradicional como con el módulo de Punto de Venta (POS).

Este módulo ha sido validado con éxito en el entorno oficial de pruebas de la AEAT (VeriFactu SOAP).

⚠️ En caso de cambios futuros en la normativa técnica o fiscal, podrían requerirse actualizaciones.
    """,
   'depends': ['base', 'point_of_sale', 'account', 'stock', 'base_setup'],
    "data": [
        # Datos y seguridad
        "data/attachments.xml",
        "security/ir.model.access.csv",

        # Crons / server actions
        "data/ir_cron.xml",
        #"data/ir_cron_verifactu.xml",
        "data/verifactu_update_checker_cron.xml",
        "data/server_actions.xml",

        # Vistas de factura
        "views/invoice/account_move_views.xml",
        "views/invoice/account_move_tree_verifactu.xml",
        "views/invoice/account_move_operation_date.xml",
        "views/invoice/qr/account_invoice_report_qr.xml",

        # Wizards
        "views/wizards/no_verifactu_requirement_wizard.xml",
        "views/wizards/verifactu_error_codes_wizard.xml",
        "views/wizards/verifactu_help_wizard.xml",
      
        # Configuración
        "views/config/res_config_settings.xml",

        # POS
        "views/pos/pos_receipt_qr_notebook.xml",
        "views/pos/pos_js.xml",
    ],
    "qweb": [
        "static/src/xml/pos_qr_template.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "OPL-1",
    "images": ["static/description/img/screenshot.png"],
}
