
{
    'name': 'Clean Data',
    'version': '15.0.0.1',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'http://www.smart-bn.com',
    'category': 'tools',
    'license': 'LGPL-3',
    'depends': [
        'base_setup',
        'web',
        'mail',
        'iap',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/app_theme_config_settings_views.xml',

    ],
    'installable': True,
    'application': True,
}
