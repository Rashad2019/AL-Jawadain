# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import date,datetime
from odoo import api,fields,models
import xlwt
from xlwt import easyxf
import io
import logging

_logger = logging.getLogger(__name__)

try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')


class VisitWizard(models.TransientModel):
    _name = 'customer.visit.report.wizard'
    _description = "Visits Wizard"

    start_dt = fields.Date('Start Visit Date')
    end_dt = fields.Date('End Visit Date')
    sh_start_dt = fields.Date('Start Show Date')
    sh_end_dt = fields.Date('End Show Date')
    company_id = fields.Many2one('res.company',string='Company',required=True,default=lambda self: self.env.company)
    zone_id = fields.Many2one('partner.zone',string='Zone',required=True)
    customer_ids = fields.Many2one("res.partner", string="Customer", domain="[('customer_rank', '>', 0)]",check_company=True)

    visit_type = fields.Selection(
        selection=[
            ('1','New Order'),
            ('2', 'Visit'),
            ('3','Collection'),
            ('4','Return'),
        ], string='Visit Purpose')
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('assigned','Assigned'),
            ('waiting','Waiting'),
            ('done', 'Done')
        ], string='Visit State')

    user_id = fields.Many2one(comodel_name="res.users",
                              string="Salesperson",
                              domain=lambda self: [("groups_id","in",
                                                    self.env.ref("sales_team.group_sale_salesman").id)
                                                   ]
                              ,check_company=True)

    def print_pdf_report(self):
        data = {'company_id': self.company_id,'date_start': self.start_dt,'date_stop': self.end_dt,
                'sh_start_dt': self.sh_start_dt,'sh_end_dt':self.sh_end_dt,
                'customer_ids':self.customer_ids,'zone_id':self.zone_id,'visit_type':self.visit_type,'state':self.state,
                'user_id': self.user_id}
        return self.env.ref('smart_visit_report.action_customer_visit_report').report_action(self)

    def print_excel_report(self):

        import base64
        filename = 'Visits_Report.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')  # 36pt
        worksheet = workbook.add_sheet('Sheet 1')
        num_style = easyxf(num_format_str='#,##0')
        num_bold = easyxf('font:bold on',num_format_str='#,##0',)
        heading_style = easyxf(
            'font:name Arial, bold on,height 350, color  dark_green; align: vert centre, horz center ;')
        heading_style1 = easyxf(
            'font:name Arial, bold on,height 250, color  dark_green; align: vert centre, horz center ;')
        first_col = worksheet.col(0)
        first_col.width = 256 * 30
        second_col = worksheet.col(1)
        second_col.width = 256 * 30
        three_col = worksheet.col(2)
        three_col.width = 256 * 30
        four_col = worksheet.col(3)
        four_col.width = 256 * 30
        five_col = worksheet.col(4)
        five_col.width = 256 * 30
        six_col = worksheet.col(5)
        six_col.width = 256 * 30
        seven_col = worksheet.col(6)
        seven_col.width = 256 * 30
        visit_types = dict(
            self.env['customer.visit'].fields_get(["visit_type"],['selection'])['visit_type']["selection"])
        visit_states = dict(
            self.env['customer.visit'].fields_get(["state"],['selection'])['state']["selection"])
        small_heading_style = easyxf(
            'font:  name  Century Gothic, bold on, color white , height 230 ; pattern: pattern solid,fore-colour dark_green; align: vert centre, horz center ;')
        medium_heading_style = easyxf(
            'font:name Arial, bold on,height 250, color  dark_green; align: vert centre, horz center ;')
        bold = easyxf('font: bold on ')
        title_report = self.zone_id.name
        if self.user_id:
            title_report = title_report +' - '+self.user_id.name
        worksheet.write_merge(0,3,0,3,_('Visits Report') + ' - ' + title_report,heading_style1)
        if self.start_dt or self.end_dt:
            visit_date_st = ''
            if self.start_dt:
                visit_date_st =_('From: ') + str(self.start_dt)
            if self.end_dt:
                visit_date_st =_(' To:') + str(self.end_dt)
            worksheet.write_merge(5,7,0,3,_('Visit Date ') + ' ' + visit_date_st,heading_style1)
        if self.sh_start_dt or self.sh_end_dt:
            send_date_st = ''
            if self.sh_start_dt:
                send_date_st =_(' From:') + str(self.sh_start_dt)
            if self.sh_end_dt:
                send_date_st =_(' To:') + str(self.sh_end_dt)
            worksheet.write_merge(8,10,0,3,_('Send Date ') + ' ' + send_date_st,heading_style1)
        if self.customer_ids:
            customers_names = ', '.join(self.customer_ids.mapped('name'))
            worksheet.write_merge(11,13,0,3,_('Customer(s)') + ' ' + customers_names,heading_style1)
        if self.visit_type or self.state:
            type_st = ''
            visit_type_str = ''
            visit_state_str = ''
            if self.visit_type:
                visit_type_str = _(visit_types[self.visit_type]) or ""
                type_st =_('Visit Type: ') + visit_type_str
            if self.state:
                visit_state_str = _(visit_states[self.state]) or ""
                type_st =_(' Visit State: ') + visit_state_str
            worksheet.write_merge(14,16,0,3,_('Type ') + ' ' + type_st,heading_style1)
        worksheet.write(17,0,_('Customer'),small_heading_style)
        worksheet.write(17,1,_('Sales Person'),small_heading_style)
        worksheet.write(17,2,_('Zone'),small_heading_style)
        worksheet.write(17,3,_('Visit Type'),small_heading_style)
        worksheet.write(17,4,_('Visit State'),small_heading_style)
        worksheet.write(17,5,_('Send Date'),small_heading_style)
        worksheet.write(17,6,_('Visit Data'),small_heading_style)
        zone_names = False
        user_names = False
        customers_names = False
        visit_type_str = False
        domain = []


        if self.start_dt:
            domain = [
                ('visit_date','>=',self.start_dt),
            ]
        if self.end_dt:
            domain = [
                ('visit_date','<=',self.end_dt),
            ]
        if self.sh_start_dt:
            domain = [
                ('show_date','>=',self.sh_start_dt),
            ]
        if self.sh_end_dt:
            domain = [
                ('show_date','<=',self.sh_end_dt),
            ]
        if self.zone_id:
            domain = [
                ('zone_id','=',self.zone_id.id),
            ]
            zone_names = self.zone_id.name
        if self.user_id:
            domain = [
                ('user_id','=',self.user_id.id),
            ]
            user_names = self.user_id.name
        if self.visit_type:
            visit_type_str = _(visit_types[self.visit_type]) or ""
            domain = [
                ('visit_type','=',self.visit_type),
            ]
        if self.state:
            domain = [
                ('state','=',self.state),
            ]
        if self.customer_ids:
            domain = [
                ('visit_ids','=',self.customer_ids.id),
            ]
            customers_names = ', '.join(self.customer_ids.mapped('name'))
        visits = self.env['customer.visit'].search(domain)



        r = 20
        total = 0
        data = {}

        if visits:
            for visit in visits:
                r = r + 1
                visit_type_str = ""
                visit_type_str = _(visit_types[visit.visit_type]) or ""
                visit_state_str = ""
                visit_state_str = _(visit_states[visit.state]) or ""
                worksheet.write(r,0,visit.visit_ids.name)
                worksheet.write(r,1,visit.user_id.name)
                worksheet.write(r,2,visit.zone_id.name)
                worksheet.write(r,3,visit_type_str)
                worksheet.write(r,4,visit_state_str)
                worksheet.write(r,5,visit.show_date.strftime("%Y-%m-%d"))
                worksheet.write(r,6,visit.visit_date.strftime("%Y-%m-%d"))


        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['visit.excel.report'].create({
            'excel_file': base64.encodestring(fp.getvalue()),
            'file_name': filename})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'visit.excel.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True


class VisitExcelReport(models.TransientModel):
    _name = "visit.excel.report"
    _description = "Visit Excel Report"

    excel_file = fields.Binary('Visit Excel Report',readonly=True)
    file_name = fields.Char('Excel File',size=64,readonly=True)
