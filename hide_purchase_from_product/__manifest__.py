
{
    "name": "Hide Purchase from Product",
    "summary": """Hide Purchase from Product""",
    "version": "14.0.1.0.0",
    "category": "product",
    'website': 'https://www.smart-bt.com',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["base","stock", "sale"],
    'data': [
        'views/views.xml',
        'views/product_view.xml',
    ],
}
