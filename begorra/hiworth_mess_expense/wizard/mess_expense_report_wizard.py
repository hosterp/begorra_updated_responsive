from openerp import models, fields, api, _
from datetime import datetime


class MessExpenseReportWizard(models.TransientModel):
    
    _name = 'mess.expense.report.wizard'
    
    date_from = fields.Date('Date From')
    date_to = fields.Date("Date To")
    staff_attendance = fields.Float(string="Staff Attendance")
    labours = fields.Float(string="Labours")
    hire_drivers = fields.Float(string="Hire drivers/Operators")
    
    @api.multi
    def action_view_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
           
        }
    
        return {
            'name': 'Mess Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_mess_expense.report_mess_and_expense_detail',
            'datas': datas,
            'report_type': 'qweb-html'
        }

    @api.multi
    def action_print_report(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        
        }
    
        return {
            'name': 'Mess Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_mess_expense.report_mess_and_expense_detail',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }
    
    
    @api.multi
    def get_details(self):
        mess_expense = self.env['mess.expense'].search([('date','>=',self.date_from),('date','<=',self.date_to)])
        mess_expense_list = []
        staff_attendance = 0
        labours = 0
        hire_drivers = 0
        for mess in mess_expense:
            mess_expense_dict = {}
            if mess.date:
                mess_expense_dict.update({'date':datetime.strptime(mess.date, '%Y-%m-%d').strftime('%d-%m-%Y')})
            if mess.total_provision:
                mess_expense_dict.update({'provision':mess.total_provision})
            if mess.total_vegetables:
                mess_expense_dict.update({'vegetables':mess.total_vegetables})
            for particular in mess.particular_expense_ids:
                mess_expense_dict.update({'cooking_water':particular.cooking_water_amt})
                if particular.gas_no:
                    mess_expense_dict.update({'gas_no': particular.gas_no})
                if particular.gas_rate:
                    mess_expense_dict.update({'gas_total': particular.gas_total})
            if mess.packing_expense:
                mess_expense_dict.update({'packing_expense':mess.packing_expense})
            if mess.total_milk_curd:
                mess_expense_dict.update({'milk_curd':mess.total_milk_curd})
            if mess.non_vegetables_expense_ids:
                chicken_total = 0
                fish_total = 0
                for non_veg in mess.non_vegetables_expense_ids:
                    if non_veg.product_id.name == 'CHICKEN':
                        chicken_total +=non_veg.total
                    if non_veg.product_id.name == 'FISH':
                        fish_total +=non_veg.total
                
                mess_expense_dict.update({'chicken':chicken_total,
                                          'fish':fish_total})
            if mess.miscellaneous:
                mess_expense_dict.update({'miscellaneous':mess.miscellaneous})
            
            if mess.total_stock:
                mess_expense_dict.update({'total_stock':mess.total_stock})
                
            mess_expense_list.append(mess_expense_dict)
            
            staff_employees = self.env['hr.employee'].search([('attendance_category','=','office_staff')])

            attendance_staff = self.env['mess.attendance'].search([('date', '=', mess.date), ('attendance', '!=', 'absent'),
                                                                   ('employee_id','in',staff_employees.ids)])
            employees_labour = self.env['hr.employee'].search([('user_category','=','labour')])
            attendance_labour = self.env['mess.attendance'].search([('date', '=', mess.date), ('attendance', '!=', 'absent'),
                                                                   ('employee_id','in',employees_labour.ids)])
            employees_driver = self.env['hr.employee'].search([('attendance_category', 'in', ['taurus_driver','eicher_driver','pickup_driver','operators'])])
            attendance_driver = self.env['mess.attendance'].search(
                [('date', '=', mess.date), ('attendance', '!=', 'absent'),
                 ('employee_id', 'in', employees_driver.ids)])
            if attendance_staff:
                staff_attendance +=  len(attendance_staff)
            if attendance_labour:
                labours += len(attendance_labour)
            if attendance_driver:
                hire_drivers += len(attendance_driver)
                
        self.staff_attendance = staff_attendance
        self.labours = labours
        self.hire_drivers = hire_drivers
            
        list_new = sorted(mess_expense_list, key=lambda i: datetime.strptime(i['date'], '%d-%m-%Y'))
        return mess_expense_list
            