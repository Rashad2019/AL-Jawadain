
{
    "name": "Cash VAN and Pre Sale Access Rights",
    "summary": """Cash VAN and Pre Sale Access Rights""",
    "version": "14.0.1.0.0",
    "category": "sale",
    'website': 'https://www.smart-bt.com',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base","account","stock", "sale"],
    'data': [
        'views/views.xml',
    ],
    'post_init_hook': 'cashvan_presale_post_init',
    'uninstall_hook': "uninstall_hook",
}
