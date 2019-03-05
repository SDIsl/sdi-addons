# Copyright 2018 David Juaneda - <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'SDi-CRM: Disable default customer message.',
    "version": "11.0.1.0.1",
    'category': 'Extra tools',
    'author': 'David Juaneda',
    'summary': """
        Unchecked recipient/s in messages.""",
    'description': """
Featured of SDi-CRM.
====================

Function: uncheck by default the checkbox included in the messages to the client as the recipient.
    """,
    'license': 'AGPL-3',
    'depends': [
        'mail',
    ],
    'qweb': [
        'static/src/xml/inherit_mail_chatter_chat_composer.xml'
    ],
    'installable':True,
}
