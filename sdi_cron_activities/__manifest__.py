# -*- coding: utf-8 -*-
{
    'name': "SDi Cron Activities",
    'summary': """
    Create Activitivies periodically""",

    'description': 'Create Activities every day, week or month',

    'author': "Javier Izco, "
              "Jorge Luis Quinteros",
    'license': 'AGPL-3',

    'category': 'Extra Tools',
    'version': '11.0.1.0.1',

    'depends': [
        'mail',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/activity_planning_view.xml',
        'data/activities_cron.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
