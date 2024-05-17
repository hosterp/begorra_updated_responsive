from openerp import models, fields, api

class QuantityStatus(models.Model):

    _name = 'quantity.status'

    @api.one
    def done(self):
        self.state = 'done'

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    location_id = fields.Many2one('stock.location', 'Site')
    date = fields.Date('Create Date')
    status_line = fields.One2many('quantity.status.line', 'status_id', 'Status')
    final = fields.Boolean('Is Final')

class QuantityStatusLine(models.Model):

    _name = 'quantity.status.line'

    @api.one
    def get_diff(self):
        for l in self:
            l.difference = l.schedule - l.proposal

    status_id = fields.Many2one('quantity.status', 'Status')
    worklist_id = fields.Many2one('survey.worklist', 'Worklist')
    schedule = fields.Float('Schedule')
    proposal = fields.Float('Proposal/ Final')
    difference = fields.Float('Difference', compute="get_diff")