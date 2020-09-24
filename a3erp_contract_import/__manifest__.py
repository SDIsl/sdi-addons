# Copyright 2020 SDi (https://www.sdi.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Importador de contratos",
    "summary": "Importador de contratos",
    "version": "12.0.0.0",
    "category": "Accounting",
    "author":
        "Sergio Lop Sanz",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "contract",
    ],
    "external_dependencies": {
        "python": [
            "xlrd",
        ]
    },
    "data": [
        "wizards/importar.xml",
    ]
}
