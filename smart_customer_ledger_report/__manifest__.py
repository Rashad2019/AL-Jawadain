
{
    'name': 'Customer Ledger Report',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 90,
    'summary': 'Customer Ledger Report by SalesPerson',
    'website': 'https://www.smart-bt.net',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'description': "",
    'depends': [
        'sale',
        'account_reports',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/models_view.xml',
        'wizard/customer_ledger_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
