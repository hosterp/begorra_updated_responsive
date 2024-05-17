from openerp import models,fields,api

class StaffMovement(models.Model):

    _name = 'staff.movement'

    @api.one
    def done(self):
        self.state = 'done'

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', 'Person', domain="[('user_category', '=', 'suplevels')]")
    location_id = fields.Many2one('stock.location', 'Site')
    purpose_id = fields.Many2one('movement.purpose', 'Purpose')
    remark = fields.Char('Remarks')

class MovementPurpose(models.Model):

    _name = 'movement.purpose'
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')