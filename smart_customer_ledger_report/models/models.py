
from odoo import api, fields, models, _
from datetime import datetime


class ResPartner(models.Model):
	_inherit ='res.partner'

	def _easy_date(self,time=False):
		now = fields.Datetime.now()
		diff = now
		if type(time) is str:
			time = fields.Datetime.from_string(time)
		if type(time) is int:
			diff = now - datetime.fromtimestamp(time)
		elif isinstance(time,datetime):
			diff = now - time
		elif not time:
			diff = now - now

		second_diff = diff.seconds
		day_diff = diff.days

		if day_diff < 0:
			return ''

		if day_diff == 0:
			if second_diff == 0:
				return ""
			if second_diff < 10:
				return _("just now")
			if second_diff < 60:
				return str(second_diff) + _(" seconds ago")
			if second_diff < 120:
				return _("a minute ago")
			if second_diff < 3600:
				return str(int(second_diff / 60)) + _(" minutes ago")
			if second_diff < 7200:
				return _("an hour ago")
			if second_diff < 86400:
				return str(int(second_diff / 3600)) + _(" hours ago")
		if day_diff == 1:
			return _("Yesterday")
		if day_diff < 7:
			return str(day_diff) + _(" days ago")
		if day_diff < 31:
			return str(int(day_diff / 7)) + _(" weeks ago")
		if day_diff < 365:
			return str(int(day_diff / 30)) + _(" months ago")
		return str(int(day_diff / 365)) + _(" years ago")


	# @api.depends('total_paid',
	# 			 'total_invoiced')
	# def _compute_total_paid_rate(self):
	# 	for partner in self:
	# 		credit = partner.total_invoiced
	# 		total_paid = partner.total_paid
	# 		total_paid_rate = 0.0
	# 		if total_paid and total_paid > 0:
	# 			if credit and credit > 0:
	# 				total_paid_rate = total_paid / credit
	# 		partner.total_paid_rate = total_paid_rate
	#
	# def _compute_total_paid(self):
	# 	for partner in self:
	# 		total_paid = 0.0
	# 		customer_balance = 0.0
	# 		payments = self.env['account.payment'].search([('partner_id','=',partner.id),('payment_type','=','inbound')],limit=1,order='data desc')
	# 		if payments:
	# 			for payment in payments:
	# 				total_paid += payment.amount
	# 		partner.total_paid = total_paid

	def _compute_total_last_paid(self):
		for partner in self:
			total_paid = 0.0
			total_invoice = 0.0
			total_paid_rate = 0.0
			date_last_paid = False
			payments = self.env['account.payment'].search([('partner_id','=',partner.id),('payment_type','=','inbound'),('move_id','!=',False)],limit=1,order='id desc')
			if payments:
				for payment in payments:
					total_paid += payment.amount
					total_invoice += payment.move_id.amount_total
					date_last_paid = payment.create_date
			partner.total_last_paid = total_paid
			if total_paid > 0 and total_invoice > 0:
				total_paid_rate = total_paid / total_invoice
			partner.total_last_paid_rate = total_paid_rate
			partner.date_last_paid = date_last_paid
			partner.date_last_paid_chr = self._easy_date(date_last_paid)
			partner.total_last_paid_rate_chr ="{0} {1}".format(round(total_paid_rate * 100),"%")

	def _compute_total_invoiced(self):
		for partner in self:
			credit = 0.0
			invoives_count = 0
			date_last_invoiced = False
			invoices = self.env['account.move'].search([('partner_id','=',partner.id),('move_type','=','out_invoice'),('state','=','posted')])
			if invoices:
				last_invoice = len(invoices)
				for invoice in invoices:
					invoives_count = invoives_count + 1
					credit += invoice.amount_total
					if invoives_count == last_invoice:
						date_last_invoiced = invoice.create_date

			partner.total_invoiced = credit
			partner.date_last_invoiced = date_last_invoiced
			partner.date_last_invoiced_chr = self._easy_date(date_last_invoiced)


	# total_paid_rate = fields.Float(string='Total Paid Rate', compute='_compute_total_paid_rate', digits='Payroll Rate')
	# total_paid = fields.Float(string='Total Paid', compute='_compute_total_paid', digits='Payroll Rate')
	total_last_paid = fields.Float(string='Last Paid', compute='_compute_total_last_paid',default=0.0, digits='Payroll Rate')
	date_last_paid = fields.Date(string='Last Paid Date', compute='_compute_total_last_paid')
	date_last_paid_chr = fields.Char(string='Last Paid Date', compute='_compute_total_last_paid')

	total_last_paid_rate_chr = fields.Char(compute='_compute_total_last_paid',string='Last Paid Rate (%)')

	total_last_paid_rate = fields.Float(string='Last Paid Rate', compute='_compute_total_last_paid', default=0.0, digits='Payroll Rate')

	total_invoiced = fields.Float(string='Total Invoiced', compute='_compute_total_invoiced', default=0.0)
	date_last_invoiced = fields.Date(string='Last Sales Date', compute='_compute_total_invoiced')
	date_last_invoiced_chr = fields.Char(string='Last Sales Date', compute='_compute_total_invoiced')
