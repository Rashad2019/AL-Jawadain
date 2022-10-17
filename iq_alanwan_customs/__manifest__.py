# -*- coding: utf-8 -*-
{
    'name': "iq_alanwan_customs",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product_expiry','product','purchase','mail','own_purchase_only'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/iq_inherit_scrap_view.xml',
        'views/iq_inherit_purchase.xml',
        'views/f_inherit_production_date.xml',
        'views/f_report_expiry_lot.xml',
        'views/f_lot_wizard_expiry.xml',
        'views/f_inherit_users.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
