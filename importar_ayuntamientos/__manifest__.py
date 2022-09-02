# Copyright 2020 SDi (https://www.sdi.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Importar ayuntamientos",
    "summary": "Importador de ayuntamientos",
    "version": "12.0.0.0",
    "category": "contacts",
    "author":
        "Sergio Lop Sanz",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
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
