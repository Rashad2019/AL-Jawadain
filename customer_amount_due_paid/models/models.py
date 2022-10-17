
from odoo import api, fields, models, _


class Amountdue(models.Model):
	_inherit ='res.partner'

	@api.depends('total_paid',
				 'total_invoiced')
	def _compute_total_paid_rate(self):
		for partner in self:
			credit = partner.total_invoiced
			total_paid = partner.total_paid
			total_paid_rate = 0.0
			if total_paid and total_paid > 0:
				if credit and credit > 0:
					total_paid_rate = total_paid / credit
			partner.total_paid_rate = total_paid_rate

	def _compute_total_paid(self):
		for partner in self:
			total_paid = 0.0
			payments = self.env['account.payment'].search([('partner_id','=',partner.id),('payment_type','=','inbound')])
			if payments:
				for payment in payments:
					total_paid += payment.amount
			partner.total_paid = total_paid

	def _compute_total_invoiced(self):
		for partner in self:
			credit = 0.0
			invoives = self.env['account.move'].search([('partner_id','=',partner.id),('move_type','=','out_invoice'),('state','=','posted')])
			if invoives:
				for invoive in invoives:
					credit += invoive.amount_total
			partner.total_invoiced = credit

	total_paid_rate = fields.Float(string='Total Paid Rate', compute='_compute_total_paid_rate', digits='Payroll Rate')
	total_paid = fields.Float(string='Total Paid', compute='_compute_total_paid', digits='Payroll Rate')
	total_invoiced = fields.Float(string='Total Invoiced', compute='_compute_total_invoiced', digits='Payroll Rate')
