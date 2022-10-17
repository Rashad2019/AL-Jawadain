
{
    "name": "Specifying Sales Journal to User",
    "summary": "Specifying Sales Journal to User",
    "version": "14.0.1.0.0",
    "category": "sales",
    "author": 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'https://www.smart-bt.com',
    'license': 'AGPL-3',
    "depends": ["base", "account", "sale","iq_sales_alanwan_customs"],
    "data": [
        "views/res_users.xml",
        "views/account_payment.xml",
    ],
    "application": False,
    "auto_install": False,
    "installable": True,
}
