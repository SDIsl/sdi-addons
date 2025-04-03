{
    'name': 'Deletions',
    'version': '12.0.1.0.0',
    'summary': 'Módulo para gestionar eliminaciones masivas de datos',
    'author': 'Fernando La Chica <SIDOO Soluciones SL>',
    'category': 'Tools',
    'depends': ['base', 'queue_job'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_deletion_views.xml',
        'data/ir_config_parameter_data.xml',
        'data/ir_cron_data.xml',
        'views/ir_deletion_log_views.xml',
    ],
    'installable': True,
    'application': False,
}
