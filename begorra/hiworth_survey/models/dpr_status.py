from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class DprStatusSurvey(models.Model):
	_name = 'dpr.status.survey'
	_rec_name = 'date'

	@api.one
	def done(self):
		self.state = 'done'


	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			list = []
			date = fields.Datetime.from_string(self.date)
			record = self.search([('date', '=',str(date + relativedelta(days=-1)).split(' ')[0])])
			for i in record.dpr_status_line:
				list.append((0,0,{
					'site_id': i.site_id.id,
					'supervisor_id': i.supervisor_id.id,
					'planned_work': i.next_day_plan,
				}))
			self.dpr_status_line = list

	state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
	date = fields.Date('Date')
	dpr_status_line = fields.One2many('dpr.status.survey.line','line_id')

class DprStatusSurveyLine(models.Model):
	_name = 'dpr.status.survey.line'

	line_id = fields.Many2one('dpr.status.survey')
	site_id = fields.Many2one('stock.location','Site')
	employee_id = fields.Many2one('hr.employee', 'Person', domain="[('user_category', '=', 'suplevels')]")
	planned_work = fields.Char('Planned Work')
	todays_work = fields.Char('Todays Work Done')
	next_day_plan = fields.Char('Next Days Plan')
	target_status = fields.Char('Target Status')
	remarks = fields.Text('Remarks')