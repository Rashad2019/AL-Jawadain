
{
    'name': 'Customer Amount Due and Amount Pay Report',
    'version': '14.0.0.0',
    'category': 'Accounting',
    'summary': 'Customer Amount Due and Amount Pay Report',
    'description' :"""

        Customer Amount Due and Amount Pay Details
   
    """,
    'website': 'https://www.smart-bt.net',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'depends': ['base', 'account','account_reports', 'mail'],
    'data': [
        'views/models_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}