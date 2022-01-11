# Copyright 2020 SDi (https://www.sdi.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Importador de bancos y mandatos",
    "summary": "Importador de bancos y mandatos",
    "version": "14.0.0.0",
    "category": "Accounting",
    "author":
        "Sergio Lop Sanz",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "account_banking_mandate",
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
        ]
    },
    "data": [
        'security/ir.model.access.csv',
        "wizards/importar.xml",
    ]
}
