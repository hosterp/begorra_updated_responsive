from openerp import fields, models, api
from datetime import date
from datetime import  datetime,timedelta

class HRDashboard(models.Model):
    _name = 'hr.dashboard'

    def get_total_employee(self):
        total_employee = self.env['hr.employee'].search([])
        self.total_employee =len(total_employee)

    def get_total_supervisor(self):
        total_supervisor = self.env['hr.employee'].search([('user_category','in',['supervisor','super_trainee'])])
        self.total_supervisor = len(total_supervisor)

    def get_total_drivers(self):
        total_driver = self.env['hr.employee'].search([('user_category','in',['driver','eicher_driver','pickup_driver','lmv_driver'])])
        self.total_driver =len(total_driver)
    def get_attendance(self):
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('attendance', 'in', ['half', 'full'])])
        
        self.attendance = len(attendance)

    def get_absent(self):
        absent = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('attendance', '=', 'absent')])
        self.absent = len(absent)

        
    def get_leaves_to_approve(self):
        leaves_to_approve = self.env['hr.holidays'].search([('state','=','confirm')])
        self.leaves_to_approve = len(leaves_to_approve)
        
    def get_daily_statements(self):
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.daily_statements_approve = len(daily_statement)

    def pending_daily_statements(self):
        self.pending_daily_statement =self.total_supervisor - self.daily_statements_approve   
        
    def get_driver_daily_statements(self):
        driver_daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.driver_daily_statements = len(driver_daily_statement)
    
    def get_pending_driver_statement(self):
        self.pending_driver_statement = self.total_driver - self.driver_daily_statements  

        
    def get_site_purchases(self):
        site_purchases = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in', ['confirm'])])
        self.site_purchases = len(site_purchases)
    
    def get_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        #print 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',yesterday_date.strftime("%Y-%m-%d %H:%M:%S")
        site_purchases_yesterday = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'confirm')])
        self.site_purchases_yesterday = len(site_purchases_yesterday)

    def get_total_site_purchase_today(self):
        total_purchase = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        self.total_site_purchases_today = len(total_purchase)

    def get_total_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        total_purchase_yes = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        self.total_site_purchases_yesterday = len(total_purchase_yes)

    def get_approved_site_purchase_today(self):
        site_purchases_approved = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in', ['approved1','approved2'])])
        self.total_site_purchase_approved_today = len(site_purchases_approved)
    
    def get_approved_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        site_purchases_approved_yes =  self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in',['approved1','approved2'])])
        self.total_site_purchase_approved_yesterday = len(site_purchases_approved_yes)
    def get_events(self):
        task = self.env['event.event'].search([('date_begin', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', '=', 'initial')])
        self.events = len(task.ids)
        
    def get_tasks(self):
        task = self.env['project.task'].search([('date_start', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', 'in', ['approved','inprogress'])])
        self.tasks = len(task.ids)
        
    def get_next_day_settlement(self):
        next_day_settlement = self.env['nextday.settlement'].search([('date', '=', date.today().strftime("%Y-%m-%d"))])
        self.next_day_settlement = len(next_day_settlement)
        
    def get_prev_attendance(self):
        date_time = date.today() - timedelta(days=1)
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('attendance', 'in', ['half', 'full'])])
        self.prev_attendance = len(attendance.ids)

    def get_prev_absent(self):
        date_time = date.today() - timedelta(days=1)
        prevabsent = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('attendance', '=', 'absent')])
        self.prev_absent = len(prevabsent)


        
    def get_daily_statements_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.daily_statements_approve_prev = len(daily_statement)

    def pending_yesterday_daily_statements(self):
        self.yes_pending_daily_statement = self.total_supervisor - self.daily_statements_approve_prev

    def pending_yesterday_driver_daily_statements(self):
        self.yes_pending_driver_daily_statement = self.total_driver - self.driver_daily_statements_prev
        
    def get_driver_daily_statements_prev(self):
        date_time = date.today() - timedelta(days=1)
        driver_daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.driver_daily_statements_prev = len(driver_daily_statement)
        
    def get_todays_grr(self):
        today_goodsrr=self.env['goods.recieve.report'].search([('Date','=', date.today().strftime("%Y-%m-%d"))])
        self.todays_total_grr = len(today_goodsrr)
    
    def get_todays_total_gtn(self):
        today_total_gtn = self.env['goods.transfer.note.in'].search([('date','=',date.today().strftime("%Y-%m-%d"))])
        self.today_total_gtn = len(today_total_gtn)

    def get_todays_total_gtn_trans(self):
        today_total_gtn_trans = self.env['goods.transfer.note.in'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state','=','transfer')])
        self.total_gtn_transferred = len(today_total_gtn_trans)
    
    def get_todays_total_gtn_recieve(self):
        today_total_gtn_recieve = self.env['goods.transfer.note.in'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state','=','recieve')])
        self.today_total_gtn = len(today_total_gtn_recieve)

    def get_todays_total_mrn(self):
        today_total_mrn = self.env['material.issue.slip'].search([('date','=',date.today().strftime("%Y-%m-%d"))])
        self.todays_mrn = len(today_total_mrn)

    def get_todays_return_note(self):
        todays_return_note = self.env['material.issue.slip'].search([('date','=',date.today().strftime("%Y-%m-%d")),('is_receive','=',True)])
        self.todays_return_note = len(todays_return_note)

    def get_todays_debit_note(self):
        todays_debit_note = self.env['debit.note.supplier'].search([('date','=',date.today().strftime("%Y-%m-%d"))]) 
        self.todays_debit_note = len(todays_debit_note)

    def get_todays_purchase_order(self):
        todays_purchase_order = self.env['purchase.order'].search([('date_order','=',date.today().strftime("%Y-%m-%d"))])
        self.todays_purchase_order = len(todays_purchase_order)

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    total_employee = fields.Float(string="Total Employee",compute='get_total_employee')
    total_supervisor=fields.Float(string="Total Supervisor",compute='get_total_supervisor')
    total_driver = fields.Float(string="Total Driver",compute ='get_total_drivers')
    pending_daily_statement =fields.Float(string="pending statements",compute='pending_daily_statements')
    pending_driver_statement = fields.Float(string = "pending driver statements",compute ="get_pending_driver_statement")
    yes_pending_daily_statement = fields.Float(string ="yesterday",compute ='pending_yesterday_daily_statements')
    yes_pending_driver_daily_statement = fields.Float(string = "yesterday driver",compute="pending_yesterday_driver_daily_statements")
    attendance = fields.Float(string="Present",compute='get_attendance')
    absent = fields.Float(string='Total Absent',compute='get_absent')
    prev_absent = fields.Float(String = 'Total Absent',compute='get_prev_absent')
    leaves_to_approve = fields.Float(string="Leaves to Approve",compute='get_leaves_to_approve')
    daily_statements_approve = fields.Float(string="Daily Statement Approve", compute='get_daily_statements')
    driver_daily_statements = fields.Float(string="Driver Daily Statement Approve", compute='get_driver_daily_statements')
    site_purchases = fields.Float(string="Site Purchases",
                                           compute='get_site_purchases')
    total_site_purchases_today = fields.Float(string = "Total site purchase today",compute ="get_total_site_purchase_today")
    total_site_purchases_yesterday = fields .Float(string ="Total site purchase yesterday",compute ="get_total_site_purchase_yesterday")
    total_site_purchase_approved_today = fields.Float(string="approved purchase",compute ="get_approved_site_purchase_today")
    total_site_purchase_approved_yesterday = fields.Float(string = "approved purchase yesterday",compute ="get_approved_site_purchase_yesterday")
    site_purchases_yesterday = fields.Float(string = "Site Purchase Yesterday",compute ="get_site_purchase_yesterday")
    events = fields.Float(string="Events",compute='get_events')
    tasks = fields.Float(string="Tasks",compute='get_tasks')
    next_day_settlement = fields.Float(string="Next Day Settlement", compute='get_next_day_settlement')
    prev_attendance = fields.Float(string="Previous Day Attendances", compute='get_prev_attendance')
    daily_statements_approve_prev = fields.Float(string="Daily Statement Approve", compute='get_daily_statements_prev')
    driver_daily_statements_prev = fields.Float(string="Driver Daily Statement Approve",
                                           compute='get_driver_daily_statements_prev')

    todays_total_grr = fields.Float(string="TOTAL GRR RECEIVED",compute="get_todays_grr")
    today_total_gtn = fields.Float(string="Total Gtn",compute="get_todays_total_gtn")
    total_gtn_transferred = fields.Float(string="Total Gtn Transfered",compute="get_todays_total_gtn_trans")
    total_gtn_recieved = fields.Float(string="Total Gtn Recieved",compute="get_todays_total_gtn_recieve")
    todays_mrn = fields.Float(string="Total MRN",compute="get_todays_total_mrn")
    todays_return_note =  fields.Float(string="Total Return Note",compute="get_todays_return_note")
    todays_debit_note = fields.Float(string="Todays Debit Note",compute="get_todays_debit_note")
    todays_purchase_order = fields.Float(string="Todays Purchase Orders")

    @api.multi
    def dashboard_attendance_today(self):
        attendance = self.env['hiworth.hr.attendance'].search([('date','=',date.today().strftime("%Y-%m-%d")),('attendance','in',['half','full'])])

        return {
            'name': "Today's Attendance",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hiworth.hr.attendance',
           'domain':[('id','in',attendance.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_leave_to_approve(self):
        leaves_to_approve = self.env['hr.holidays'].search([('state', '=', 'confirm')])
        return {
            'name': "Leaves to Approve",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hr.holidays',
            'domain': [('id', 'in', leaves_to_approve.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_supervisor_daily_statement(self):
        daily_statement = self.env['partner.daily.statement'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state', 'not in', ['draft','cancelled'])])
        return {
            'name': "Today's Supervisor Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'partner.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_driver_daily_statement(self):
        daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Today's Driver Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'driver.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_purchase(self):
        total_purchase = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        return {
            'name': "Today's Purchase",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'site.purchase',
            'domain': [('id', 'in', total_purchase.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_current_inventory(self):
        
        return {
            'name': "Current Inventory Valuation",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'stock.history',
           
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_project_task(self):
        task = self.env['event.event'].search([('date_begin','<=',date.today().strftime("%Y-%m-%d")),('date_end','>=',date.today().strftime("%Y-%m-%d")),('state','=','initial')])
        
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'event.event',
            'domain':[('id','in',task.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_project_estimation(self):
        task = self.env['project.task'].search([('date_start', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', 'in', ['approved','inprogress'])])
    
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'project.task',
            'domain': [('id', 'in', task.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_next_settlement(self):
        next_day_settlement = self.env['nextday.settlement'].search([('date', '=', date.today().strftime("%Y-%m-%d"))])
    
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'nextday.settlement',
            'domain': [('id', 'in', next_day_settlement.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_prev_attendance(self):
        date_time = date.today() - timedelta(days=1)
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=',date_time.strftime("%Y-%m-%d")) , ('attendance', 'in', ['half', 'full'])])
    
        return {
            'name': "Yesterday's Attendance",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hiworth.hr.attendance',
            'domain': [('id', 'in', attendance.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_bank_details(self):
        banks = self.env['res.partner.bank'].search(
            [('common_usage', '=', True)])
    
        return {
            'name': "Bank Details",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'res.partner.bank',
            'domain': [('id', 'in', banks.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_supervisor_daily_statement_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Yesterday's Supervisor Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'partner.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_driver_daily_statement_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Yesterday's Driver Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'driver.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }
        
    @api.multi
    def dashboard_purchase_prev(self):

        yesterday_date = date.today() - timedelta(days=1)
        total_purchase = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S"))])

        return {
            'name': "Yesterday's Purchase",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'site.purchase',
            'domain': [('id', 'in', total_purchase.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dasboard_today_grr(self):
        today_goodsrr=self.env['goods.recieve.report'].search([('Date','=', date.today().strftime("%Y-%m-%d"))])

        return {

            'name': "Goods Receive Report",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'goods.recieve.report',
            'domain': [('id', 'in', today_goodsrr.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dasboard_today_gtn(self):
        today_total_gtn = self.env['goods.transfer.note.in'].search([('date','=',date.today().strftime("%Y-%m-%d"))])

        return {

            'name': "Goods Transfer Note",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'goods.transfer.note.in',
            'domain': [('id', 'in', today_total_gtn.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dasboard_today_mrn(self):
        today_total_mrn = self.env['material.issue.slip'].search([('date','=',date.today().strftime("%Y-%m-%d"))])

        return {

            'name': "MATERIAL REQUISITION NOTE",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'material.issue.slip',
            'domain': [('id', 'in', today_total_mrn.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dasboard_today_return_note(self):
        todays_return_note = self.env['material.issue.slip'].search([('date','=',date.today().strftime("%Y-%m-%d")),('is_receive','=',True)])

        return {

            'name': "MATERIAL RETURN NOTE",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'material.issue.slip',
            'domain': [('id', 'in', todays_return_note.ids)],
            'type': 'ir.actions.act_window'
        }


    @api.multi
    def dasboard_today_debit_note(self):
        todays_debit_note = self.env['debit.note.supplier'].search([('date','=',date.today().strftime("%Y-%m-%d"))])

        return {

            'name': "DEBIT NOTE SUPPLIER",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'debit.note.supplier',
            'domain': [('id', 'in', todays_debit_note.ids)],
            'type': 'ir.actions.act_window'
        }


    @api.multi
    def dasboard_today_purchase_order(self):
        todays_purchase_order = self.env['purchase.order'].search([('date_order','=',date.today().strftime("%Y-%m-%d"))])

        return {

            'name': "Purchase Order",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'purchase.order',
            'domain': [('id', 'in', todays_purchase_order.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def todays_stock_report(self):
        view = self.env.ref('hiworth_construction.form_report_location_stock_daily')
        #context = self.env.context
        return {
         'name':'Name',
         'type': 'ir.actions.act_window',
         'view_type': 'form',
         'view_mode': 'form',
         'res_model': 'report.location.stock.daily',
         'views': [(view.id, 'form')],
         'view_id': view.id,
         'target': 'new',
         'context':{'default_date_today':date.today().strftime("%Y-%m-%d")}
        }