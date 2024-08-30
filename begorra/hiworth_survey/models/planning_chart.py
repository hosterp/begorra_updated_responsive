from openerp import models,fields,api

class SurveyPlanningChart(models.Model):

    _name = "survey.planning.chart"

    @api.one
    def done(self):
        self.state = 'done'

    is_weekly = fields.Boolean('Is Weekly')
    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    period_from = fields.Date('Period From')
    period_to = fields.Date('Period To')
    is_site = fields.Boolean('Is Site')
    chart_lines = fields.One2many('survey.planning.chart.line', 'survey_id')

class SurveyPlanningChartLine(models.Model):

    _name = "survey.planning.chart.line"

    survey_id = fields.Many2one('survey.planning.chart')
    create_date = fields.Date('Created On')
    location_id = fields.Many2one('stock.location', 'Site')
    worklist_id = fields.Many2one('survey.worklist', 'Work List')
    employee_id = fields.Many2one('hr.employee', 'Concerned Person', domain="[('user_category', '=', 'suplevels')]")
    completion_date = fields.Date('Proposed Completion Date')
    completed_on = fields.Date('Actual Completion Date')

class SurveyWorkList(models.Model):

    _name = "survey.worklist"
    _rec_name = 'name'

    name = fields.Char('Name')
    code = fields.Char('Code')