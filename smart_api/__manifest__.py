
{
    'name': "Smart API",
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'category': 'Tools',
    'summary': """Smart VAN API """,
    'website': 'https://www.smart-bt.net',
    'license': 'AGPL-3',
    'description': """ """,
    'version': '1.0',
    'depends':  ['base', 'account', 'sale','hr_attendance_geolocation','customer_approved','base_geolocalize','iq_sales_alanwan_customs','iq_extend_sales_alanwan_customs','specify_journal_to_user','specify_inventory_to_user','cashvan_presale','sale_discount_limit','customer_visits','return_period_invoice'],
    'data': [
        'security/smart_api_security.xml',
        'security/ir.model.access.csv',
        'views/smart_api_views.xml',
        'views/res_config_form.xml',
        'views/hr_attendance_view.xml',

    ],
    'application': True,
    'auto_install': False,
    'installable': True,

}
