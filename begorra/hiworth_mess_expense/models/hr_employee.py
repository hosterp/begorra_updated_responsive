from openerp import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    @api.multi
    def load_employee_mess_attendance(self):
        # for employee in self:
        #     recs = self.env['hiworth.hr.attendance'].search([('name','=',employee.id)])
        #     last_rec = recs and max(recs)
        return {
            'name': self[0].name,
            'view_mode': 'form,tree',
            'res_model': 'mess.attendance',
            'type': 'ir.actions.act_window',
            "views": [
                [self.env.ref("hiworth_mess_expense.mess_attendance_form_view").id, "form"]],
            'domain': [('employee_id', '=', self[0].id)],
            "context": {'default_employee_id': self[0].id},}
