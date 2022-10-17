

{
	"name": "Commissions Report",
	"summary": "Commissions Repor",
	"version": "14.0.1.0.0",
	"category": "sales",
	"author": 'RASHAD ALKHAWLANI - SMART BUSINESS TECH ',
	'website': 'https://www.smart-bt.com',
	'license': 'AGPL-3',
	"depends": ["sales_team","sale_commission_salesman"],
	"data": [
		'security/ir.model.access.csv',
		'wizard/report_commission.xml',
		'wizard/commission_wizard_view.xml',


	],
	"auto_install": False,
	"installable": True,
}
