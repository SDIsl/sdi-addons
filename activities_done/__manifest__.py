# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name':'SDi-CRM: actived activities',
    "version": "11.0.1.0.1",
    'category':'Uncategorized',
    'author':'David Juaneda',
    'summary': """  
        Save activities done.""",
    'license':'AGPL-3',
    'depends':[
        'activities_board',
        'activities_sync_event',
    ],
    'data':[
        'views/inherit_calendar_event_views.xml',
        'views/inherit_mail_activity_views.xml',
        'views/inherit_view_crm_case_opportunities_filters.xml',
        'views/inherit_view_res_partner_filters.xml',
    ],
    'installable': True,
}
