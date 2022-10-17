
{
    'name': 'Custom Invoice Report',
    'version': '14.0.1.0.1',
    'category': 'Sales',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'http://www.smart-bt.com',
    'license': 'LGPL-3',
    'depends': [
        'account','sale','iq_po_discount_custom','iq_extend_sales_alanwan_customs'
    ],
    'data': [
        'data/paper_format.xml',
        'report/custom_invoice_templates.xml',
        'report/account_report.xml',
        'views/account_move_form.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True
}
