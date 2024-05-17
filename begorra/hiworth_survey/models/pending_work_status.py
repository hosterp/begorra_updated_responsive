from openerp import models, fields, api

class PendingWorkStatus(models.Model):

    _name = 'survey.pending.work.status'

    @api.one
    def done(self):
        self.state = 'done'

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    location_id = fields.Many2one('stock.location', 'Site Name')
    worklist_id = fields.Many2one('survey.worklist', 'Work List')
    employee_id = fields.Many2one('hr.employee', 'Person', domain="[('user_category', '=', 'suplevels')]")
    remarks = fields.Char('Remarks')
    is_site = fields.Boolean('Is Site')
