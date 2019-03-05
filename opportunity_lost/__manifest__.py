# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "SDi-CRM: lost opportunity",
    'license': 'AGPL-3',
    'summary': """
         Improvements in lost opportunities.""",
    'description': """
    - Add description to the reason for the loss of an opportunity.
    - Add a smartButton in customers' form view that counts the number of lost opportunities and linking to them. 
    """,
    'author': [
        "David Juaneda",
        "Manuel Muñoz",
    ],
    'category': 'Extra tools',
    "version": "11.0.1.0.1",
    'depends': [
        'crm',
    ],
    'data': [
        'wizard/wizard.xml',
        'views/inherit_res_partner_views.xml',
    ],
    'installable': True,
}

