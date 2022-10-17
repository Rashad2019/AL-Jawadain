# -*- coding: utf-8 -*-
from odoo import models, fields, api
import datetime





class iq_lotreport_custom(models.Model):
    _name = 'iq.lot.expiry.wizard'
    
    
    def get_default_date(self):
        print("222")
        cur_date = datetime.datetime.now().date()
        self.iq_date = cur_date
        return cur_date
        
        
        
        
    iq_days_beforeexpiry = fields.Integer("Days Before Expired ",default=7)
    iq_date = fields.Datetime('Date',default=get_default_date)
    
    
    def iq_create_activity(self):
        cur_date = datetime.datetime.now().date()
        new_date = cur_date + datetime.timedelta(days=7)
        ids = self.env['stock.production.lot'].search([('expiration_date','>=',cur_date),('expiration_date','<=',new_date)])
        activity_vals = []
        
        
        for eco in ids:
           
                print("2222211111",eco.name)
                for user in self.env['res.users'].search([('f_recevielotnotfiy','=',True)]):
                        activity_vals.append({
                                                'activity_type_id': self.env['mail.activity.type'].search([('name','=','Alert Date Reached')]).id,
                                                'user_id': user.id,
                                                'res_id': eco.id,
                                                'res_model_id': self.env.ref('stock.model_stock_production_lot').id,
                                                'date_deadline':eco.expiration_date.strftime("%Y-%m-%d"),
                                                'summary':'Soon Expiration Date'
                                                
                                            })
                                    
                            
        
        print("activity_vals",activity_vals)           
        self.env['mail.activity'].create(activity_vals)
    
    def iq_get_product_expired(self):
        print("11111111",self.iq_days_beforeexpiry)
        
        cur_date = self.iq_date
        new_date = cur_date + datetime.timedelta(days=self.iq_days_beforeexpiry)
        
        ids = self.env['stock.production.lot'].search([('expiration_date','<',cur_date)])
        groupss= {}
        for a in ids :
            dic_name = a.id
            if not groupss.get(dic_name):
                groupss[dic_name] = {}
                groupss[dic_name].update({
                        'name': a.name,
                        'product':a.product_id.name,
                        'ex_date':a.expiration_date,
                        'qty':a.product_qty,
                       
                    })
                
                
        data = {
            'iq_days_beforeexpiry': self.iq_days_beforeexpiry,
            'iq_date': self.iq_date,
            'lot_no':groupss,
        }
        
        
        return self.env.ref('iq_alanwan_customs.iq_lot_expiry_receipt').report_action(self,data=data)
    
    
    def iq_get_product_alertexpired(self):
        print("11111111",self.iq_days_beforeexpiry)
        
        cur_date = self.iq_date
        new_date = cur_date + datetime.timedelta(days=self.iq_days_beforeexpiry)
        
        ids = self.env['stock.production.lot'].search([('expiration_date','>=',cur_date),('expiration_date','<=',new_date)],order='expiration_date asc')
        
        groupss= {}
        for a in ids :
            dic_name = a.id
            if not groupss.get(dic_name):
                groupss[dic_name] = {}
                groupss[dic_name].update({
                        'name': a.name,
                        'product':a.product_id.name,
                        'ex_date':a.expiration_date,
                        'qty':a.product_qty,
                       
                    })
                
                
        data = {
            'iq_days_beforeexpiry': self.iq_days_beforeexpiry,
            'iq_date': self.iq_date,
            'lot_no':groupss,
        }
        
        
        print("data",data)
        return self.env.ref('iq_alanwan_customs.iq_lot_expiry_receipt').report_action(self,data=data)
    
    