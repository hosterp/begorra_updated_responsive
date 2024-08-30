from openerp import models, fields, api, _


class MessExpense(models.Model):
    _name = 'mess.attendance'
    
    
    
        
    employee_id = fields.Many2one('hr.employee',string="Name")
    date = fields.Date(string="Date")
    attendance = fields.Selection([('absent','Absent'),
                                   ('half','Half Present'),
                                   ('full','Full Present')],string="Attendance")
    
    
  
class MessReportExpense(models.Model):
    _name = 'mess.report.attendance'

    mess_expense_id = fields.Many2one('mess.expense', string="Mess Expense")
    employee_id = fields.Many2one('hr.employee',string="Staff")
   