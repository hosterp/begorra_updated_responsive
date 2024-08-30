from openerp import models, fields,api

class WorkStatus(models.Model):

    _name = 'survey.work.status'

    @api.one
    def done(self):
        self.state = 'done'

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    location_id = fields.Many2one('stock.location', 'Site Name')
    status = fields.Selection([('level_taken', 'Levels Taken'), ('level_submitted', 'Levels Submitted')], 'state')
    report_status_line = fields.One2many('survey.work.status.line', 'status_id', 'Report Status')

class WorkStatusLine(models.Model):

    _name = 'survey.work.status.line'

    status_id = fields.Many2one('survey.work.status', 'Status')
    reporting_status = fields.Char('Reporting Status')
    reporting_date = fields.Date('Reporting Date')
    approval_status = fields.Char('Approval Status')
    approval_date = fields.Date('Approval Date')