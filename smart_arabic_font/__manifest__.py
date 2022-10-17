{
    'name': "Arabic Font",
    'summary': 'Arabic Font',
    "description":
        """ Arabic Font """,
    "author": "RASHAD ALKHAWLANI - SMART BUSINESS TECH ",
    'website': 'http://www.smart-bt.com',
    'category': 'tools',
    'version': '15.0.0.0',
    'depends': ['web'],
    'qweb': [],
    'auto_install': True,
    'installable': True,
    'assets': {
        'web.assets_common': [
            'smart_arabic_font/static/src/scss/almaraifont.scss',
            'smart_arabic_font/static/src/scss/cairofont.scss',
            'smart_arabic_font/static/src/scss/droidfont.scss',
            'smart_arabic_font/static/src/css/web_style.css',
        ],
        'web.report_assets_common': [
            'smart_arabic_font/static/src/scss/almaraifont.scss',
            'smart_arabic_font/static/src/scss/cairofont.scss',
            'smart_arabic_font/static/src/scss/droidfont.scss',
            'smart_arabic_font/static/src/css/report_style.css',

        ],

        'data': [
            # "views/linkestatic.xml",
        ],

    },
}