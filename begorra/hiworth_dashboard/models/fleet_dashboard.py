from openerp import fields, models, api
from datetime import date
from datetime import  datetime,timedelta



class HRDashboard(models.Model):
    _name = 'fleet.dashboard'


    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")

    

    @api.multi
    def monthly_report(self):
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]
    
        action['context'] = {'monthly_report': True}
        return action

    @api.multi
    def Daily_Utilization_report(self):
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]

        action['context'] = {'daily_utilisation': True}
        return action


    @api.multi
    def today_preventive_maintanence(self):
        prev_main = self.env['fleet.vehicle.log.services'].search([('date_com','=',date.today().strftime("%Y-%m-%d")),('prev_main_bool','=',True)])
        #context = self.env.context
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]

        action['context'] = {'preventive_maintenance':True}
        # return {
        #     'name': "Preventive Maintenance",
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'views': [(False, 'tree')],
        #     'view_id': self.env.ref('hiworth_tms.fleet_vehicle_log_services_tree_prev_main').id,
        #     'res_model': 'fleet.vehicle.log.services',
        #     'domain': [('id', 'in', prev_main.ids)],
        #     'type': 'ir.actions.act_window'
        # }
        return action

    @api.multi
    def daily_maintanence(self):
        daily_main = self.env['fleet.vehicle.log.services'].search([('date_com','=',date.today().strftime("%Y-%m-%d")),('daily_maint_bool','=',True)])
        #context = self.env.context
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]

        action['context'] = {'daily_maintenance':1}

        return action
    @api.multi
    def repairs_and_breakdowns(self):
        repairs_breakdown = self.env['fleet.vehicle.log.services'].search([('date_com','=',date.today().strftime("%Y-%m-%d")),('r_b_bool','=',True)])
        #context = self.env.context
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]
        # action['domain'] = [('id', 'in', repairs_breakdown.ids)]
        action['context'] = {'breakdown_report':True}

        return action

    @api.multi
    def tyre_repairs(self):
        tyre_repair_daily = self.env['fleet.vehicle.log.services'].search([('date_com','=',date.today().strftime("%Y-%m-%d")),('tyre_bool','=',True)])
        #context = self.env.context
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]

        action['context'] = {'tyre_repairs':True,
                             'tyre_bool':0}

        return action

    @api.multi
    def other_repairs(self):
        other_repair_daily = self.env['fleet.vehicle.log.services'].search([('date_com','=',date.today().strftime("%Y-%m-%d")),('other_bool','=',True)])
        #context = self.env.context
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]
        # action['domain'] = [('id', 'in', other_repair_daily.ids)]
        action['context'] = {'other_repairs':True}

        return action


    @api.multi
    def fuel_details(self):
        action = self.env.ref('hiworth_dashboard.action_report_maintanace_daily').read()[0]
        action['context'] = {'fuel_details': True}

        return action