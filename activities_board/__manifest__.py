# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'DEPRECATED SDi-CRM: activities board',
    "version": "11.0.1.0.1",
    'category': "Uncategorized",
    'author': 'David Juaneda',
    'summary': """
        Add activities board.""",
    'description': """
This is a full-featured crm system.
========================================

It supports:
------------

    - Board activities with form, tree, kanban, graph, calendar and pivot
    views and different filters.

    """,
    'license': 'GPL-3',
    'depends': [
        'crm',
        'mail',
        'board',
    ],
    'data': [
        'views/activities_boards_views.xml',
        'views/inherit_crm_opportunities_views.xml',
    ],
    'installable': True,
}
