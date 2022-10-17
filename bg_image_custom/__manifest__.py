{
    'name': "Custom Home Background Image",
    'summary': """
       Custom Home Background Image
    """,
    'description': """
        Custom Home Background Image
    """,
    'version': '14.0.1.0.1',
    'category': 'tools',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'https://www.smart-bt.com',
    'license': 'LGPL-3',
    'depends': ['base','web_enterprise'],
    'data': [
        'views/webclient.xml',
#         'views/templates.xml',
        'views/company_view.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "bg_image_custom/static/src/js/background_image.js",
        ],
    },
}
