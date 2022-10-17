# -*- coding: utf-8 -*-

from odoo import api,models,fields,_
import xlwt
from odoo.exceptions import Warning,ValidationError,UserError
import io
import base64

try:
    import xlwt
except ImportError:
    xlwt = None


class js_excel(models.TransientModel):
    _name = 'xls.excel'

    def create_excel(self,ids,model,fields_string,fields_row,selection_field):

        if len(ids) == 0:
            raise ValidationError("Please Select Records, Without Records Excel Cannot be Printed")
        else:

            models = self.env[model].browse(ids)
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            filename = model.replace('.', ' ').title() + ' Report.xls'
            values = self.env[model].search_read([('id','in',ids)],fields_row)

            selection_value = [];

            for key in selection_field:
                for value in key:
                    selection_value.append(value)

            row = 0
            for lines in fields_string:
                worksheet.write(0,row,lines,xlwt.easyxf('font:bold on'))
                worksheet.col(row).width = 7000
                row += 1

            row_2 = 2
            col_0 = 0

            for value in values:
                for lines in fields_row:
                    sql = "SELECT ttype FROM ir_model_fields ir inner join ir_model mo on (ir.model_id = mo.id) WHERE ir.name='%s' and mo.model='%s';" % (
                    str(lines),str(model));
                    try:
                        self.env.cr.execute(sql)
                        [val] = self.env.cr.fetchone()
                    except:
                        val = None
                    if lines:
                        if val == 'datetime':
                            if value[lines] == False:
                                worksheet.write(row_2,col_0,0,xlwt.easyxf("font: name Liberation Sans"))
                            else:
                                date_time = value[lines].strftime('%d-%m-%Y')
                                worksheet.write(row_2,col_0,date_time,xlwt.easyxf("font: name Liberation Sans"))

                        elif val == 'date':
                            if value[lines] == False:
                                worksheet.write(row_2,col_0,0,xlwt.easyxf("font: name Liberation Sans"))
                            else:
                                date_time = value[lines].strftime('%d-%m-%Y')
                                worksheet.write(row_2,col_0,date_time,xlwt.easyxf("font: name Liberation Sans"))

                        elif val == 'selection':
                            for values in selection_value:
                                if value[lines] == values[0]:
                                    worksheet.write(row_2,col_0,values[1],xlwt.easyxf("font: name Liberation Sans"))
                                    break

                        elif val == 'many2one' and isinstance(value[lines],tuple):
                            worksheet.write(row_2,col_0,value[lines][1],xlwt.easyxf("font: name Liberation Sans"))
                        elif val == 'float':
                            worksheet.write(row_2,col_0,round(value[lines],2),xlwt.easyxf("font: name Liberation Sans"))

                        else:
                            worksheet.write(row_2,col_0,value[lines],xlwt.easyxf("font: name Liberation Sans"))

                        col_0 += 1
                row_2 += 1
                col_0 = 0

        fp = io.BytesIO()
        workbook.save(fp)
        export_id = self.env['sale.excel'].create(
            {'excel_file': base64.encodestring(fp.getvalue()),'file_name': filename})
        fp.close()
        return export_id.id


class js_pdf(models.TransientModel):
    _name = 'export.pdf'

    def create_pdf(self,ids,model,fields_string,fields_row,selection_field):

        if len(ids) == 0:
            raise ValidationError("Please Select Records, Without Records Excel Cannot be Printed")
        else:

            models = self.env[model].browse(ids)
            filename = 'Detail Report.pdf'
            values = self.env[model].search_read([('id','in',ids)],fields_row)

            selection_value = [];
            headers_title = [];
            lines_data = []
            for key in selection_field:
                for value in key:
                    selection_value.append(value)

            row = 0
            for lines in fields_string:
                headers_title.append(lines)
                row += 1

            row_2 = 2
            col_0 = 0

            for value in values:
                line_data = []
                for lines in fields_row:
                    sql = "SELECT ttype FROM ir_model_fields ir inner join ir_model mo on (ir.model_id = mo.id) WHERE ir.name='%s' and mo.model='%s';" % (
                        str(lines),str(model));
                    try:
                        self.env.cr.execute(sql)
                        [val] = self.env.cr.fetchone()
                    except:
                        val = None
                    if lines:
                        print(val)
                        if val == 'datetime':
                            if value[lines] == False:
                                # worksheet.write(row_2,col_0,0,xlwt.easyxf("font: name Liberation Sans"))
                                line_data.append('')
                            else:
                                date_time = value[lines].strftime('%d-%m-%Y')
                                # worksheet.write(row_2,col_0,date_time,xlwt.easyxf("font: name Liberation Sans"))
                                line_data.append(date_time)

                        elif val == 'date':
                            if value[lines] == False:
                                # worksheet.write(row_2,col_0,0,xlwt.easyxf("font: name Liberation Sans"))
                                line_data.append('')
                            else:
                                date_time = value[lines].strftime('%d-%m-%Y')
                                # worksheet.write(row_2,col_0,date_time,xlwt.easyxf("font: name Liberation Sans"))
                                line_data.append('')

                        elif val == 'selection':
                            for values in selection_value:
                                if value[lines] == values[0]:
                                    # worksheet.write(row_2,col_0,values[1],xlwt.easyxf("font: name Liberation Sans"))
                                    line_data.append(values[1])
                                    break

                        elif val == 'many2one' and isinstance(value[lines],tuple):
                            # worksheet.write(row_2,col_0,value[lines][1],xlwt.easyxf("font: name Liberation Sans"))
                            line_data.append(value[lines][1])

                        elif val == 'float':
                            line_data.append(round(value[lines], 2))
                        else:
                            # worksheet.write(row_2,col_0,value[lines],xlwt.easyxf("font: name Liberation Sans"))
                            line_data.append(value[lines])

                lines_data.append(line_data)

        reportdata = {'model': model,
                      'headers_title': headers_title,
                      'lines_data': lines_data}
        return reportdata

class sale_excel(models.TransientModel):
    _name = "sale.excel"

    excel_file = fields.Binary('Excel Report',readonly=True)
    file_name = fields.Char('Excel File',size=64)


class PrintListPdf(models.AbstractModel):
    _name = 'report.list_export_excel_app.report_list_pdf'


    @api.model
    def _get_report_values(self,docids, data=None):
        if not "model" in data:

            raise UserError(
                _("Form content is missing, \
                  this report cannot be printed."))
        model = data["model"]
        docs = self.env[model].browse([])

        return {
            'doc_ids': docs.ids,
            'doc_model': self.env[model],
            'docs': docs,
            'data': data,
        }
