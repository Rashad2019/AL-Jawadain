
from odoo import api, fields, models, _


class VisitReport(models.AbstractModel):

	_name='report.smart_visit_report.visit_report'
	_description ="Visit Report"
	
	def _get_report_values(self, docids, data=None,sessions=False):
		zone_names = False
		user_names = False
		customers_names = False
		visit_type_str = False
		visit_state_str = False

		domain = []
		visit_report_rec = self.env['customer.visit.report.wizard'].browse(docids)
		visit_types = dict(
			self.env['customer.visit'].fields_get(["visit_type"],['selection'])['visit_type']["selection"])
		visit_states = dict(
			self.env['customer.visit'].fields_get(["state"],['selection'])['state']["selection"])

		if visit_report_rec and visit_report_rec.start_dt:
			domain = [
				('visit_date','>=',visit_report_rec.start_dt),
				('visit_date','<=',visit_report_rec.end_dt),
			]
		if visit_report_rec and visit_report_rec.end_dt:
			domain = [
				('visit_date','<=',visit_report_rec.end_dt),
			]
		if visit_report_rec and visit_report_rec.sh_start_dt:
			domain = [
				('show_date','>=',visit_report_rec.sh_start_dt),
			]
		if visit_report_rec and visit_report_rec.sh_end_dt:
			domain = [
				('show_date','<=',visit_report_rec.sh_end_dt),
			]
		if visit_report_rec and visit_report_rec.zone_id:
			domain = [
				('zone_id','=',visit_report_rec.zone_id.id),
			]
			zone_names = visit_report_rec.zone_id.name
		if visit_report_rec and visit_report_rec.user_id:
			domain = [
				('user_id','=',visit_report_rec.user_id.id),
			]
			user_names = visit_report_rec.user_id.name
		if visit_report_rec and visit_report_rec.visit_type:
			visit_type_str = _(visit_types[visit_report_rec.visit_type]) or ""
			domain = [
				('visit_type','=',visit_report_rec.visit_type),
			]
		if visit_report_rec and visit_report_rec.state:
			visit_state_str = _(visit_states[visit_report_rec.state]) or ""
			domain = [
				('state','=',visit_report_rec.state),
			]
		if visit_report_rec and visit_report_rec.customer_ids:
			domain = [
				('visit_ids','=',visit_report_rec.customer_ids.id),
			]
			customers_names = ', '.join(visit_report_rec.customer_ids.mapped('name'))
		visits = self.env['customer.visit'].search(domain)
		visits_data =[]
		if visits:
			for visit in visits:
				data_visit_type_str = ""
				data_visit_type_str = _(visit_types[visit.visit_type]) or ""
				data_visit_state_str = ""
				data_visit_state_str = _(visit_states[visit.state]) or ""
				visit_data = {
					'customer': visit.visit_ids.name,
					'salesperson': visit.user_id.name,
					'zone': visit.zone_id.name,
					'visit_type':data_visit_type_str,
					'visit_state':data_visit_state_str,
					'visit_date': visit.visit_date,
					'show_date': visit.show_date,

				}
				visits_data.append(visit_data)
		return {
			'currency_precision': 2,
			'doc_ids': docids,
			'doc_model': 'customer.visit.report.wizard',
			'start_dt': visit_report_rec.start_dt or False,
			'end_dt': visit_report_rec.end_dt or False,
			'sh_start_dt': visit_report_rec.sh_start_dt or False,
			'sh_end_dt': visit_report_rec.sh_end_dt or False,
			'zone_names': zone_names or False,
			'user_names': user_names or False,
			'customers_names': customers_names or False,
			'visit_type': visit_type_str or False,
			'visit_state':visit_state_str or False,
			'visits_data': visits_data or [],
			'company_id': self.env.company,
		}
