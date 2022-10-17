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


class CommissionWizard(models.TransientModel):
    _name = 'commission.report.wizard'
    _description = "Commission Wizard"

    start_dt = fields.Date('Start Date')
    end_dt = fields.Date('End Date')
    company_id = fields.Many2one('res.company',string='Company',required=True,default=lambda self: self.env.company)
    product_id = fields.Many2many('product.product',string='Product', domain=[('commission_free', '=', False)])

    user_ids = fields.Many2many(comodel_name="res.users",
                              string="Salesperson",
                              domain=lambda self: [("groups_id","in",
                                                    self.env.ref("sales_team.group_sale_salesman").id)
                                                   ]
                              ,check_company=True)

    def print_pdf_report(self):
        data = {'company_id': self.company_id,'start_dt': self.start_dt,'end_dt': self.end_dt,
                'product_id':self.product_id,'user_ids': self.user_ids}
        return self.env.ref('smart_commission_report.action_commission_report').report_action(self)

    def print_excel_report(self):

        import base64
        filename = 'Target_Commissions_Report.xls'
        workbook = xlwt.Workbook()
        style = xlwt.XFStyle()
        tall_style = xlwt.easyxf('font:height 720;')  # 36pt
        worksheet = workbook.add_sheet('Sheet 1')
        num_style = easyxf(num_format_str='#,##0')
        num_bold = easyxf('font:bold on',num_format_str='#,##0',)
        bold_style = easyxf('font:bold on',)

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
        total_style = easyxf(
            'font:  name  Century Gothic, bold on, color dark_green , height 230 ; pattern: pattern solid,fore-colour white; align: vert centre, horz center ;')

        small_heading_style = easyxf(
            'font:  name  Century Gothic, bold on, color white , height 230 ; pattern: pattern solid,fore-colour dark_green; align: vert centre, horz center ;')
        medium_heading_style = easyxf(
            'font:name Arial, bold on,height 250, color  dark_green; align: vert centre, horz center ;')
        bold = easyxf('font: bold on ')
        usernames = ''
        if self.user_ids:
            usernames = ' - '.join(self.user_ids.mapped('name'))
            worksheet.write_merge(0,3,0,3,_('Target Commission Report') + ' ( ' + usernames + ' ) ',heading_style1)
        else:
            worksheet.write_merge(0,3,0,4,_('Target Commission Report'),heading_style1)
        if self.start_dt or self.end_dt:
            visit_date_st = ''
            if self.start_dt:
                visit_date_st =_('From: ') + str(self.start_dt)
            if self.end_dt:
                visit_date_st =_(' To:') + str(self.end_dt)
            worksheet.write_merge(5,7,0,4,_('Date ') + ' ' + visit_date_st,heading_style1)
        if self.product_id:
            products_names = ' - '.join(self.product_id.mapped('name'))
            worksheet.write_merge(8,10,0,4,_('Products') + ' ( ' + products_names + ' ) ',heading_style1)
        worksheet.write(12,0,_('Sales Person'),small_heading_style)
        worksheet.write(12,1,_('Product'),small_heading_style)
        worksheet.write(12,2,_('Target Quantity'),small_heading_style)
        worksheet.write(12,3,_('Achievement Rate %'),small_heading_style)
        worksheet.write(12,4,_('Total Sales'),small_heading_style)
        worksheet.write(12,5,_('Target Total'),small_heading_style)
        worksheet.write(12,6,_('Total Commission'),small_heading_style)

        domain = [('settled','=',False)]


        if self.start_dt:
            domain += [
                ('date_invoice','>=',self.start_dt),
            ]
        if self.end_dt:
            domain += [
                ('date_invoice','<=',self.end_dt),
            ]

        self.env['sale.commission.analysis.report'].sudo().init()
        commissions = self.env['sale.commission.analysis.report'].sudo().search(domain)
        sale_order_groupby_dict = {}
        if self.user_ids:
            for salesperson in self.user_ids:
                filtered_sale_order = list(filter(lambda x: x.agent_id == salesperson.partner_id, commissions))
                if self.product_id:
                    filtered_by_product = list(filter(lambda x: x.product_id in self.product_id, filtered_sale_order))
                    sale_order_groupby_dict[salesperson.id] = filtered_by_product
                else:
                    sale_order_groupby_dict[salesperson.id] = filtered_sale_order
        else:
            for salesperson in commissions.mapped('agent_id'):
                filtered_sale_order = list(filter(lambda x: x.agent_id == salesperson,commissions))
                if self.product_id:
                    filtered_by_product = list(filter(lambda x: x.product_id in self.product_id,filtered_sale_order))
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
                target_total = 0.0
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
                    agent_product = self.env['product.product.agent'].sudo().search([('product_id', '=', order.product_id.id),('agent', '=', order.agent_id.id)])

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
                        target_total = 0
                        target_achivement = 0.0

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

        r = 14
        total = 0
        data = {}

        if final_dist:
            for salespersons in final_dist.keys():

                total_amount = 0.0
                salesperson_name = ''
                for commission_product in final_dist[salespersons].values():
                    # commission_product = final_dist[salespersons][commissions]
                    if commission_product:
                            total_amount = total_amount + commission_product['amount']
                            salesperson_name = commission_product['agent_name']
                            r = r + 1
                            worksheet.write(r,0,commission_product['agent_name'],bold_style)
                            worksheet.write(r,1,commission_product['product_name'],bold_style)
                            worksheet.write(r,2,commission_product['target'],bold_style)

                            worksheet.write(r,3,commission_product['target_achivement_rate'],bold_style)
                            worksheet.write(r,4,commission_product['total'],bold_style)
                            worksheet.write(r,5,commission_product['target_total'],bold_style)
                            worksheet.write(r,6,commission_product['amount'],bold_style)
                if salesperson_name != '':
                    r = r + 4
                    total_amount = round(total_amount,2)

                    worksheet.write_merge(r-1,r+1,0,6,_('Total Commission for  ') + salesperson_name + ' = ' + str(total_amount),total_style)
                    r = r + 2

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['commission.excel.report'].create({
            'excel_file': base64.encodestring(fp.getvalue()),
            'file_name': filename})
        fp.close()
        return {
            'view_mode': 'form',
            'res_id': export_id.id,
            'res_model': 'commission.excel.report',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        return True


class CommissionExcelReport(models.TransientModel):
    _name = "commission.excel.report"
    _description = "Commission Excel Report"

    excel_file = fields.Binary('Commission Excel Report',readonly=True)
    file_name = fields.Char('Excel File',size=64,readonly=True)
