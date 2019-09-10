# -*- coding: utf-8 -*-
{
    'name': "SDi Notification Activities",
    'summary': """
    Add notifications funtions to Activitivies to notify when an activity ends""",
    'description': 'Add notifications functions to activities',
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
        'data/mail_activity_data.xml',
        'views/inherit_mail_activity.xml',
        'views/activity_notifs_templates.xml',
    ],
    'qweb': ['static/src/xml/base_activity_notifs.xml'],
    'installable': True,
}
