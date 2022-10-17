# -*- coding: utf-8 -*-
{
    'name': 'Export and Print List View for All Application',
    'version': '14.0.1.0',
    'category': 'tools',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'https://www.smart-bt.com',
    'description': """Export and Print (EXCEL/PDF) List View for All Application""",
    'license': 'OPL-1',
    'depends': ['base','base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/excel.xml',
    ],
    'qweb': ['static/src/xml/custom_button.xml'],
    'installable': True,
    'auto_install': False,
}
