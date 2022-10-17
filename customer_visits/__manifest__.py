
{
    "name": "Customer Visits",
    "summary": "Customer Visits",
    "version": "15.0.1.0.0",
    "category": "sales",
    "author": 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
    'website': 'https://www.smart-bt.com',
    'license': 'AGPL-3',
    "depends": ["base", "sale","crm","smart_partner_zone"],
    "qweb": ['static/src/xml/openstreetmap_visits_template.xml'],
    "data": [
        "security/ir.model.access.csv",
#         "views/assets.xml",
        "views/res_partners.xml",
        "views/views.xml",
        "views/crm_lead_visits.xml",
        "views/crm_multi_tasks.xml",
        "views/sale_order_form.xml",
        "views/res_config_form.xml",
        "data/cron.xml"

    ],
    "assets": {
        "web.assets_backend": [
            "customer_visits/static/src/js/openstreetmap_visit_widget.js",
        ],
    },
    "application": False,
    "auto_install": False,
    "installable": True,
}
