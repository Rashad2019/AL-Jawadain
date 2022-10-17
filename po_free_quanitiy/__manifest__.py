# -*- coding: utf-8 -*-
{
    'name': "po_free_quantity",

    'summary': """
        Add free Quantity on Purchase Order lines
        """,

    'description': """
        Add free Quantity on Purchase Order lines
    """,
    'version': '14.0.1.0.0',
    'category': 'tools',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'http://www.smart-bt.com',
    'depends': ['purchase','purchase_stock','stock'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
    ],

}
