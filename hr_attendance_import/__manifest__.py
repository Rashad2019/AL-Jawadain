
{
    'name': 'Attendances_Import',
    'category': 'Human Resources',
    'summary': 'Import employee attendances',
    'description': """
    Import employee attendances from csv file
       """,

    'version': '14.0.1.0.0',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'http://www.smart-bt.com',
    'license': 'AGPL-3',
    'depends': ['hr_attendance'],
    'application': False,
    'installable': True,
    'data': [
        'security/hr_attendance_import_security.xml',
        'security/ir.model.access.csv',
        'wizards/hr_attendance_import_view.xml',
        'wizards/hr_attendance_fix_employee_view.xml',
        'wizards/hr_attendance_search_checkout_view.xml',
        'views/hr_attendance_incidence_view.xml',
        'views/menu.xml',
    ],
}
