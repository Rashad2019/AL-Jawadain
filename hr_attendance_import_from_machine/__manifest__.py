
{
    "name": "Import Attendance Data From Machine CSV",
    "version": "14.0.1.0.0",
    "category": "tools",
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'http://www.smart-bt.com',
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_attendance_machine_views.xml",
        "wizards/hr_attendance_import.xml",
    ],
}
