from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class ResPartnerVisit(models.Model):
    _name = 'customer.visit'

    def _default_user_id(self):
        if not self.user_id:
            return self.env.user
        return False


    def _default_visit_ids(self):
        if self._context['active_model'] == 'res.partner' and not self.visit_ids:
            customer = self.env['res.partner'].browse(self._context['active_id'])
            if customer:
                return customer
            else:
                return False
        else:
            return False

    def _default_valid_user_ids(self):

        valid_user_ids = self.env['res.users'].sudo().browse()

        return valid_user_ids.mapped('id')

    def _default_valid_customrs_ids(self):

        valid_customrs_ids = self.env['res.partner'].sudo().search([('customer_rank','>',0)])

        return valid_customrs_ids.mapped('id')



    visit_ids = fields.Many2one("res.partner", string="Customer", domain="[('customer_rank', '>', 0)]")
    profile_id = fields.Many2one("customer.visit.wizard",store=True,ondelete='restrict', string="Profile")
    profile_line_id = fields.Many2one("customer.visit.wizard.line",store=True, string="Profile Line")

    display_name = fields.Char(compute='_compute_display_name')
    zone_id = fields.Many2one('partner.zone',string='Zone',store=True)

    visit_date = fields.Date(string="Visit Date",default=fields.Date.today())
    show_date = fields.Date(string="Show Task Date",default=fields.Date.today())

    assigned_by = fields.Many2one(comodel_name="res.users", string="Assigned by", default=_default_user_id, )
    visit_type = fields.Selection(
        selection=[
            ('1','New Order'),
            ('2', 'Visit'),
            ('3','Collection'),
            ('4','Return'),
            ('5','By Salesperson'),

        ],default='5', string='Visit Purpose')
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('assigned','Assigned'),
            ('waiting','Waiting'),
            ('done', 'Done')
        ], default='draft', string='Visit State',tracking=1, track_visibility='onchange')

    user_id = fields.Many2one(comodel_name="res.users",
                              string="Salesperson",
                              tracking=1,
                              domain=lambda self: [("groups_id","in",
                                                    self.env.ref("sales_team.group_sale_salesman").id)
                                                   ]
                              )

    @api.depends('zone_id')
    def _compute_valid_user_ids(self):
        for visit in self:
            valid_users_domain =[]
            if visit.zone_id:
                valid_users_domain += [('zone_id', 'in', visit.zone_id.ids)]
            # if visit.visit_ids.salesperson_ids:
            #     valid_users_domain += [('id','in',visit.visit_ids.salesperson_ids.ids)]
            valid_user_ids = self.env['res.users'].sudo().search(valid_users_domain)
            visit.valid_user_ids = valid_user_ids.mapped('id')

    @api.depends('user_id','zone_id')
    def _compute_valid_customrs_ids(self):
        for visit in self:
            visit.valid_customrs_ids = self.env['res.partner']
            customers_domain = [('customer_rank','>',0)]
            if visit.user_id:
                customers_domain += [('salesperson_ids','in',visit.user_id.id)]
                if visit.user_id.zone_id:
                    customers_domain += [('zone_id','in',[visit.zone_id.id])]
                salesperson_customers = self.env['res.partner'].sudo().search(customers_domain)
                visit.valid_customrs_ids = salesperson_customers.mapped('id')


    valid_customrs_ids = fields.Many2many("res.partner",
                              string="Sales person Customers",
                              default=_default_valid_customrs_ids,
                              compute=_compute_valid_customrs_ids,
                              domain=[('customer_rank', '>', 0)],
                                      )


    valid_user_ids = fields.Many2many("res.users",
                              string="Valid Sales person",
                              default=_default_valid_user_ids,
                              compute=_compute_valid_user_ids,
                              domain=lambda self: [
                                  ('groups_id','in',self.env.ref('sales_team.group_sale_salesman').id)],

                                      )


    meeting_person_name = fields.Char(string="Person Name",  required=False, )
    meeting_person_phone = fields.Char(string="Person Phone",  required=False, )
    reason_visit = fields.Char(string="Visit Reason",  required=False, )
    result_visit = fields.Char(string="Visit Result",  required=False, )
    is_assigned_next_visit = fields.Boolean(string="Is assigned Next Visit Date?")
    next_visit = fields.Date(string="Next Visit Date", required=False, )
    latitude = fields.Float(
        "Visit Latitude", digits="Location"
    )
    longitude = fields.Float(
        "Visit Longitude", digits="Location"
    )
    street = fields.Char(string='Address')
    map = fields.Char(string='map')

    @api.onchange('user_id','zone_id')
    def _onchange_salesperson(self):
        customers_domain = []
        if self.user_id:
            customers_domain += [('salesperson_ids','in',self.user_id.id)]
            if self.user_id.zone_id:
                customers_domain += [('zone_id', 'in', [self.zone_id.id])]
            salesperson_customers = self.env['res.partner'].sudo().search(customers_domain)
            self.visit_ids = salesperson_customers.mapped('id')


    @api.onchange('visit_ids')
    def _onchange_customer(self):
        if self.visit_ids:
            self.write({'meeting_person_name':self.visit_ids.display_name,'meeting_person_phone':self.visit_ids.phone,'street': self.visit_ids.street})
            if not self.latitude:
                self.write({'latitude':self.visit_ids.partner_latitude})
            if not self.longitude:
                self.write({'longitude': self.visit_ids.partner_longitude})
            # if self.user_id and self.user_id not in self.valid_user_ids:
            #     self.user_id = False

    @api.onchange('zone_id')
    def _onchange_zone(self):
        customers_domain = []
        if self.zone_id:
            self.user_id = False
            self.visit_ids = False
            self._compute_valid_user_ids()
            self._compute_valid_customrs_ids()

    def button_done(self):
        self.write({"state": "done"})

    def button_waiting(self):
        self.write({"state": "waiting"})

    def button_draft(self):
        self.write({"state": "draft", "user_id": False})

    def button_assigned(self):
        if not self.user_id:
            raise ValidationError("Please Select Salesperson, Without Salesperson Visit State Can not be Assigned")
        self.write({"state": "assigned"})

    @api.depends('visit_ids')
    def _compute_display_name(self):
        for cat in self:
            if cat.visit_ids:
                cat.display_name = cat.visit_ids.display_name
            else:
                cat.display_name = _('New Visit')


    @api.model
    def create(self, vals):
        if 'visit_ids' in vals and 'visit_type' in vals:
            partnerObj = self.env['res.partner'].sudo()
            invoiceObj = self.env['account.move'].sudo()
            action_date = fields.date.today()
            customer = partnerObj.search([('id','=',vals['visit_ids'])])
            if vals['visit_type'] == '3':
                if customer and 'risk_invoice_unpaid' in partnerObj._fields :
                    if customer.risk_invoice_unpaid == 0:
                        raise ValidationError(_("(%s) does not have unpaid invoices to collect",customer.name))
            if vals['visit_type'] == '4':
                if customer and 'no_of_days_to_return' in invoiceObj._fields :
                    invoices = invoiceObj.search(
                        [('payment_state','!=','reversed'),('move_type','in',['out_invoice']),('state','=','posted'),
                         ('partner_id','=',customer.id)]). \
                        filtered(lambda move: (move.invoice_date + datetime.timedelta(
                        days=move.no_of_days_to_return)) > action_date)
                    if not invoices:
                        raise ValidationError(_("(%s) does not have returnable invoices",customer.name))
                        # raise ValidationError(_("The customer does not have returnable invoices"))
        return super(ResPartnerVisit, self).create(vals)

    def write(self,vals):
        if 'visit_ids' in vals and 'visit_type' in vals:
            partnerObj = self.env['res.partner'].sudo()
            invoiceObj = self.env['account.move'].sudo()
            action_date = fields.date.today()
            customer = partnerObj.search([('id','=',vals['visit_ids'])])
            if vals['visit_type'] == '3':
                if customer and 'risk_invoice_unpaid' in partnerObj._fields :
                    if customer.risk_invoice_unpaid == 0:
                        raise ValidationError(_("(%s) does not have unpaid invoices to collect",customer.name))
            if vals['visit_type'] == '4':
                if customer and 'no_of_days_to_return' in invoiceObj._fields :
                    invoices = invoiceObj.search(
                        [('payment_state','!=','reversed'),('move_type','in',['out_invoice']),('state','=','posted'),
                         ('partner_id','=',customer.id)]). \
                        filtered(lambda move: (move.invoice_date + datetime.timedelta(
                        days=move.no_of_days_to_return)) > action_date)
                    if not invoices:
                        raise ValidationError(_("(%s) does not have returnable invoices",customer.name))
        elif 'visit_ids' in vals and 'visit_type' not in vals:
            partnerObj = self.env['res.partner'].sudo()
            invoiceObj = self.env['account.move'].sudo()
            action_date = fields.date.today()
            customer = partnerObj.search([('id','=',vals['visit_ids'])])
            if self.visit_type == '3':
                if customer and 'risk_invoice_unpaid' in partnerObj._fields :
                    if customer.risk_invoice_unpaid == 0:
                        raise ValidationError(_("(%s) does not have unpaid invoices to collect",customer.name))
            if self.visit_type == '4':
                if customer and 'no_of_days_to_return' in invoiceObj._fields :
                    invoices = invoiceObj.search(
                        [('payment_state','!=','reversed'),('move_type','in',['out_invoice']),('state','=','posted'),
                         ('partner_id','=',customer.id)]). \
                        filtered(lambda move: (move.invoice_date + datetime.timedelta(
                        days=move.no_of_days_to_return)) > action_date)
                    if not invoices:
                        raise ValidationError(_("(%s) does not have returnable invoices",customer.name))

        elif 'visit_ids' not in vals and 'visit_type' in vals:
            partnerObj = self.env['res.partner'].sudo()
            invoiceObj = self.env['account.move'].sudo()
            action_date = fields.date.today()
            customer = partnerObj.search([('id','=',self.visit_ids.id)])
            if vals['visit_type'] == '3':
                if customer and 'risk_invoice_unpaid' in partnerObj._fields :
                    if customer.risk_invoice_unpaid == 0:
                        raise ValidationError(_("The customer does not have unpaid invoices"))
            if vals['visit_type'] == '4':
                if customer and 'no_of_days_to_return' in invoiceObj._fields :
                    invoices = invoiceObj.search(
                        [('payment_state','!=','reversed'),('move_type','in',['out_invoice']),('state','=','posted'),
                         ('partner_id','=',customer.id)]). \
                        filtered(lambda move: (move.invoice_date + datetime.timedelta(
                        days=move.no_of_days_to_return)) > action_date)
                    if not invoices:
                        raise ValidationError(_("The customer does not have returnable invoices"))

        res = super(ResPartnerVisit,self).write(vals)
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    visits_ids = fields.One2many("customer.visit", "visit_ids", string="Customer Visits", required=False, )

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    visits_ids = fields.One2many("customer.visit", compute='_compute_visits_ids', string="Customer Visits", )

    @api.onchange("partner_id")
    def onchange_partner_id_visits_ids(self):
        if self.partner_id.visits_ids:
            self.visits_ids = self.partner_id.visits_ids

    def _compute_visits_ids(self):
        if self.partner_id.visits_ids:
            self.visits_ids = self.partner_id.visits_ids
        else:
            self.visits_ids = False


class CustomerVisitsWizardLine(models.Model):
    _name = "customer.visit.wizard.line"

    profile_id = fields.Many2one("customer.visit.wizard",readonly=True,store=True, ondelete="cascade",string="Profile")

    @api.depends('profile_id','profile_id.zone_id','profile_id.user_id')
    def _compute_valid_customrs_ids(self):
        for visit in self:
            visit.valid_customrs_ids = self.env['res.partner']
            customers_domain = [('customer_rank','>',0)]
            if visit.profile_id.user_id:
                customers_domain += [('salesperson_ids','in',visit.profile_id.user_id.id)]
                if visit.profile_id.zone_id:
                    customers_domain += [('zone_id','in',[visit.profile_id.zone_id.id])]
                salesperson_customers = self.env['res.partner'].sudo().search(customers_domain)
                visit.valid_customrs_ids = salesperson_customers.mapped('id')


    valid_customrs_ids = fields.Many2many("res.partner",string="Customers",compute=_compute_valid_customrs_ids)
    customrs_ids = fields.Many2one("res.partner",string="Customer")
    visit_date = fields.Date(string="Visit Date")
    send_to_salesperson = fields.Boolean(string="Send to SalesPerson",default=False)
    every_week = fields.Boolean(string="Every Week in this Month",default=False)

    _sql_constraints = [
        ('check_visit_date', "CHECK(send_to_salesperson == True AND visit_date IS NULL)", 'Require a Visit Date '),
    ]

    visit_type = fields.Selection(
        selection=[
            ('1','New Order'),
            ('2', 'Visit'),
            ('3','Collection'),
            ('4','Return'),
            ('5','By Salesperson'),
        ],default='5', string='Visit Purpose')


class CustomerVisitsWizard(models.Model):
    _name = "customer.visit.wizard"
    _description = "Customers Visit Wizard"

    zone_id = fields.Many2one('partner.zone',string='Zone',store=True)

    visit_ids = fields.Many2many("res.partner", string="Customers", domain="[('customer_rank', '>', 0)]")
    user_id = fields.Many2one(comodel_name='res.users',string='Salesperson',
               domain=lambda self: [("groups_id","=",
                             self.env.ref("sales_team.group_sale_salesman").id)
                                    ]
                               )

    def _default_user_id(self):
        if not self.user_id:
            return self.env.user
        return False


    assigned_by = fields.Many2one(comodel_name="res.users", string="Assigned by", default=_default_user_id, )

    def _default_valid_customrs_ids(self):

        valid_customrs_ids = self.env['res.partner'].sudo().search([('customer_rank','>',0)])

        return valid_customrs_ids.mapped('id')

    @api.depends('user_id','zone_id')
    @api.onchange('user_id','zone_id')
    def _compute_valid_customrs_ids(self):
        self.valid_customrs_ids = False
        self.visit_line_ids = False
        for visit in self:
            visit.valid_customrs_ids = self.env['res.partner']
            customers_domain = [('customer_rank','>',0)]
            if visit.user_id:
                customers_domain += [('salesperson_ids','in',visit.user_id.id)]
                if visit.zone_id:
                    customers_domain += [('zone_id','in',[visit.zone_id.id])]
                salesperson_customers = self.env['res.partner'].sudo().search(customers_domain)
                visit.valid_customrs_ids = salesperson_customers
                visit.visit_line_ids = False
                visit.visit_line_ids = [(0,0,{'profile_id':visit.id,'customrs_ids': customer,'visit_type': '2'}) for customer in salesperson_customers.mapped('id')]


    def _default_valid_user_ids(self):

        valid_user_ids = self.env['res.users'].sudo().browse()

        return valid_user_ids.mapped('id')


    @api.depends('zone_id')
    def _compute_valid_user_ids(self):
        for visit in self:
            visit.valid_user_ids = False
            valid_users_domain = []
            if visit.zone_id:
                valid_users_domain += [('zone_id', 'in', visit.zone_id.id)]
            valid_user_ids = self.env['res.users'].sudo().search(valid_users_domain)
            visit.valid_user_ids = valid_user_ids.mapped('id')



    valid_user_ids = fields.Many2many("res.users",
                              string="Valid Sales person",
                              default=_default_valid_user_ids,
                              compute=_compute_valid_user_ids,
                              domain=lambda self: [
                                  ('groups_id','in',self.env.ref('sales_team.group_sale_salesman').id)],

                                      )
    valid_customrs_ids = fields.Many2many("res.partner",
                              "customer_visit_wizard_valid_customrs_ids",
                              "profile_id",
                              string="Sales person Customers",
                              default=_default_valid_customrs_ids,
                              # compute=_compute_valid_customrs_ids,
                              domain=[('customer_rank', '>', 0)],
                                      )

    visit_line_ids = fields.One2many("customer.visit.wizard.line","profile_id",store=True,string="Customers")

    @api.onchange('visit_line_ids')
    def _onchange_visit_line_ids(self):
        if self.visit_line_ids:
            print('_onchange_visit_line_ids')
            # self.create_tasks()
            self._compute_visits_count()

    @api.onchange('zone_id')
    def _onchange_zone(self):
        customers_domain = []
        if self.zone_id:
            self.user_id = False
            self.visit_ids = False
            self._compute_valid_user_ids()
            self._compute_valid_customrs_ids()

    @api.onchange('user_id','zone_id')
    def _onchange_salesperson(self):
        customers_domain = []
        if self.user_id:
            customers_domain += [('salesperson_ids','in',self.user_id.id)]
            if self.user_id.zone_id:
                customers_domain += [('zone_id', 'in', [self.zone_id.id])]
            salesperson_customers = self.env['res.partner'].sudo().search(customers_domain)
            self.visit_ids = salesperson_customers.mapped('id')
        else:
            self.visit_ids = False



    visit_date = fields.Date(string="Visit Date",default=fields.Date.today())
    show_date = fields.Date(string="Show Task Date",default=fields.Date.today())
    visit_type = fields.Selection(
        selection=[
            ('1','New Order'),
            ('2', 'Visit'),
            ('3','Collection'),
            ('4','Return'),
        ],default='2', string='Visit Purpose')
    display_name = fields.Char(compute='_compute_display_name')
    visits_count = fields.Integer(default=0,compute='_compute_visits_count')

    def _compute_visits_count(self):
        for cat in self:
            visits_domain = [('profile_id','=',cat.id),('state','in',['assigned','done'])]
            visits_count = self.env['customer.visit'].sudo().search_count(visits_domain)
            cat.visits_count = visits_count

    @api.depends('user_id','visit_type','visit_date')
    def _compute_display_name(self):
        for cat in self:
            if cat.user_id:
                cat.display_name = "{} - {}".format(
                    cat.user_id.name,
                    cat.zone_id.name,
                )
            else:
                cat.display_name = _('New Profile Routes')

    def show_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Visits',
            'view_mode': 'tree,form',
            'res_model': 'customer.visit',
            'context': {'default_user_id': self.env.user.id},
            'domain': [('profile_id','=',self.id),('state','in',['assigned','done'])],
        }

    def daterange(self,date1,date2):
        for n in range(int((date2 - date1).days) + 1):
            yield date1 + timedelta(n)

    def last_day_of_month(self,date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month + 1,day=1) - datetime.timedelta(days=1)

    def create_tasks_next_months(self):
        task_obj = self.env['customer.visit'].sudo()
        routes_obj = self.env['customer.visit.wizard'].sudo().search([])
        print('create_tasks_next_months')
        for route_obj in routes_obj:
            for customer in route_obj.visit_line_ids.filtered(lambda line: line.every_week):
                visit_id = route_obj.id
                visit_line_id = customer.id

                state = 'waiting'
                if customer.send_to_salesperson:
                    state = 'assigned'
                visit_data = {
                    'visit_ids': customer.customrs_ids.id,
                    'user_id': route_obj.user_id.id,
                    'zone_id': route_obj.zone_id.id or False,
                    'assigned_by': route_obj.env.user.id,
                    # 'visit_date': self.visit_date,
                    'visit_date': customer.visit_date,
                    'show_date': route_obj.show_date,
                    'visit_type': '5',
                    'state': state,
                    'latitude': customer.customrs_ids.partner_latitude,
                    'longitude': customer.customrs_ids.partner_longitude,
                    'meeting_person_name': customer.customrs_ids.display_name,
                    'meeting_person_phone': customer.customrs_ids.phone,
                    'street': customer.customrs_ids.street,
                    'profile_id': visit_id,
                    'profile_line_id': visit_line_id,
                }
                if customer.every_week and customer.visit_date:
                    next_month = customer.visit_date + relativedelta(months=1)
                    weekday = next_month.weekday()
                    end_dt = self.last_day_of_month(next_month)
                    for dt in self.daterange(next_month,end_dt):
                        routes = task_obj.search([('profile_line_id','=',visit_line_id),('profile_id','=',visit_id),
                                                  ('visit_ids','=',customer.customrs_ids.id),('visit_date','=',dt)])

                        if dt.weekday() == weekday and not routes:
                            visit_data['visit_date'] = dt
                            visit_data['show_date'] = dt + relativedelta(days=-5)
                            task_obj.sudo().create(visit_data)


    def create_tasks(self):

        task_obj = self.env['customer.visit']
        for customer in self.visit_line_ids:
            visit_id = str(self.id).replace('NewId_','')
            visit_line_id = str(customer.id).replace('NewId_','')

            state = 'waiting'
            if customer.send_to_salesperson:
                state = 'assigned'
            routes = task_obj.search([('profile_line_id','=',visit_line_id),('profile_id','=',visit_id),('visit_ids','=',customer.customrs_ids.id)])
            if customer.send_to_salesperson and not routes:
                visit_data = {
                    'visit_ids': customer.customrs_ids.id,
                    'user_id': self.user_id.id,
                    'zone_id': self.zone_id.id or False,
                    'assigned_by': self.env.user.id,
                    # 'visit_date': self.visit_date,
                    'visit_date': customer.visit_date,
                    'show_date': self.show_date,
                    'visit_type': '5',
                    'state': state,
                    'latitude': customer.customrs_ids.partner_latitude,
                    'longitude': customer.customrs_ids.partner_longitude,
                    'meeting_person_name': customer.customrs_ids.display_name,
                    'meeting_person_phone': customer.customrs_ids.phone,
                    'street': customer.customrs_ids.street,
                    'profile_id': visit_id,
                    'profile_line_id': visit_line_id,
                }
                task_obj.create(visit_data)
                if customer.every_week and customer.visit_date:
                    weekday = customer.visit_date.weekday()
                    end_dt = self.last_day_of_month(customer.visit_date)
                    for dt in self.daterange(customer.visit_date,end_dt):
                        if dt.weekday() == weekday and dt > customer.visit_date:  # to print only the weekdates
                            visit_data['visit_date'] = dt
                            task_obj.create(visit_data)

            if routes:
                for route in routes.filtered(lambda routec: routec.state != 'done'):
                    if customer.send_to_salesperson:
                        route.write({'state': 'assigned'})
                    else:
                        route.write({'state': 'waiting'})
        # return {'type': 'ir.actions.act_window_close'}

        return {
            'type': 'ir.actions.act_window',
            'name': 'Customer Visits',
            'view_mode': 'tree,form',
            'res_model': 'customer.visit',
            'context': {'default_user_id': self.env.user.id},
            'domain': [('profile_id','=',self.id)],

        }