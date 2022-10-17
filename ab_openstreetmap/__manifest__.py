{
    'name': "Openstreetmap Widget",
    'summary': """
       Openstreetmap Widget
    """,
    'description': """
        Show Openstreetmap in Form View
        Required for works add a lat long field to the model
    """,
    'version': '14.0.1.0.1',
    'category': 'Sales',
    'author': 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'https://www.smart-bt.com',
    'license': 'LGPL-3',
    'depends': ['base','base_geolocalize'],
    "qweb": ['static/src/xml/openstreetmap_template.xml'],
    'data': [
#         'views/templates.xml',
        'views/partnet_view.xml'
    ],
    "assets": {
        "web.assets_backend": [
            "ab_openstreetmap/static/src/css/Control.Geocoder.css",
            "ab_openstreetmap/static/src/css/leaflet.css",
            "ab_openstreetmap/static/src/js/leaflet.js",
            "ab_openstreetmap/static/src/js/Control.Geocoder.js",
            "ab_openstreetmap/static/src/js/openstreetmap_widget.js",
        ],
    },
}
