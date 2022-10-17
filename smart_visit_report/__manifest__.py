

{
	"name": "Customer Visits Report",
	"summary": "Customer Visits",
	"version": "14.0.1.0.0",
	"category": "sales",
	"author": 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
	'website': 'https://www.smart-bt.com',
	'license': 'AGPL-3',
	"depends": ["customer_visits"],
	"data": [
		'security/ir.model.access.csv',
		'wizard/report_visit.xml',
		'wizard/visit_wizard_view.xml',

	],
	"auto_install": False,
	"installable": True,
}
