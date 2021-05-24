# -*- coding: utf-8 -*-
{
    'name': "SDi Add Notification to Activities Planning",
    'summary': """
    Add notifications funtions to Activitivies to notify when an activity
    ends""",

    'description': 'Add notifications functions to activities',

    'author': "Javier Izco, "
              "Jorge Luis Quinteros",
    'license': 'AGPL-3',

    'category': 'Extra Tools',
    'version': '11.0.1.0.1',

    'depends': [
        'resource',
        'sdi_cron_activities',
        'sdi_notification_activities',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/inherit_activity_planning_view.xml',
    ],
    'demo': [
    ],
    'application': False,
    'installable': True,
    'auto_install': True,
}
