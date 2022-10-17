
from odoo import api, fields, models, _


class CommissionReport(models.AbstractModel):

	_name='report.smart_commission_report.commission_report'
	_description ="Commission Report"
	
	def _get_report_values(self, docids, data=None,sessions=False):

		wizard_rec = self.env['commission.report.wizard'].browse(docids)

		domain = [('settled','=',False)]
		if wizard_rec.start_dt:

			domain += [
				('date_invoice','>=',wizard_rec.start_dt),
			]
		if wizard_rec.end_dt:
			domain += [
				('date_invoice','<=',wizard_rec.end_dt),
			]

		usernames = ''
		if wizard_rec.user_ids:
			usernames = ' - '.join(wizard_rec.user_ids.mapped('name'))
		products_names = ''
		if wizard_rec.product_id:
			products_names = ' - '.join(wizard_rec.product_id.mapped('name'))
		self.env['sale.commission.analysis.report'].sudo().init()
		commissions = self.env['sale.commission.analysis.report'].sudo().search(domain)
		sale_order_groupby_dict = {}
		if wizard_rec.user_ids:
			for salesperson in wizard_rec.user_ids:
				filtered_sale_order = list(filter(lambda x: x.agent_id == salesperson.partner_id,commissions))
				if wizard_rec.product_id:
					filtered_by_product = list(filter(lambda x: x.product_id in wizard_rec.product_id,filtered_sale_order))
					sale_order_groupby_dict[salesperson.id] = filtered_by_product
				else:
					sale_order_groupby_dict[salesperson.id] = filtered_sale_order
		else:
			for salesperson in commissions.mapped('agent_id'):
				filtered_sale_order = list(filter(lambda x: x.agent_id == salesperson,commissions))
				if wizard_rec.product_id:
					filtered_by_product = list(filter(lambda x: x.product_id in wizard_rec.product_id,filtered_sale_order))
					sale_order_groupby_dict[salesperson.id] = filtered_by_product
				else:
					sale_order_groupby_dict[salesperson.id] = filtered_sale_order

		final_dist = {}
		for salesperson in sale_order_groupby_dict.keys():
			sale_data = []
			prod_data = {}
			for order in sale_order_groupby_dict[salesperson]:
				target = 0.0
				target_achivement = 0.0
				product = order.product_id.id
				if product in prod_data:
					old_amount = prod_data[product]['amount']
					old_price_subtotal = prod_data[product]['total']
					target = prod_data[product]['target']
					old_quantity = prod_data[product]['target_done']
					target_achivement = ((old_quantity + order.quantity) / target) * 100
					prod_data[product].update({
						'total': float(old_price_subtotal + order.price_subtotal),
						'amount': float(old_amount + order.amount),
						'target_done': float(old_quantity + order.quantity),
						'target_achivement_rate': float(target_achivement),

					})
				else:
					agent_product = self.env['product.product.agent'].sudo().search(
						[('product_id','=',order.product_id.id),('agent','=',order.agent_id.id)])

					if agent_product:
						agent_product._compute_target_achivement()
						if agent_product.target_achivement >= agent_product.target_achivement_compute:
							target = agent_product.target
							target_achivement = (order.quantity / target) * 100
							target_total = agent_product.target * order.price_unit

						else:
							continue
					else:
						target = 0.0
						target_achivement = 0.0
						target_total = 0

					prod_data.update({product: {
						'agent_name': order.agent_id.name,
						'product_id': order.product_id.id,
						'product_name': order.product_id.name,
						'total': float(order.price_subtotal),
						'target_total': float(target_total),
						'amount': float(order.amount),
						'target_done': float(order.quantity),
						'target': float(target),
						'target_achivement_rate': float(target_achivement),

					}})
			final_dist[salesperson] = prod_data
		#
		return {
			'currency_precision': 2,
			'doc_ids': docids,
			'doc_model': 'commission.report.wizard',
			'start_dt': wizard_rec.start_dt or False,
			'end_dt': wizard_rec.end_dt or False,
			'usernames': usernames or False,
			'products_names': products_names or False,
			'final_dist': final_dist or {},
			'company_id': self.env.company,
		}
