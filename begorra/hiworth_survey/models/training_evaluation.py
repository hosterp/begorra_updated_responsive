from openerp import models, fields, api

class TrainingEvaluation(models.Model):

    _name = 'training.evaluation'

    @api.one
    def done(self):
        self.state = 'done'

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', 'Name', domain="[('user_category', '=', 'suplevels')]")
    attachment_id = fields.Binary('Attachment')
    remarks = fields.Char('Remarks')
