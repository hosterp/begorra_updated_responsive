from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class InstrumentStatus(models.Model):

    _name = 'instrument.status'

    @api.one
    def done(self):
        self.state = 'done'

    @api.onchange('duration')
    def onchange_duration(self):
        if self.calibrated_on:
            date = datetime.datetime.strptime(str(self.calibrated_on), "%Y-%m-%d")+relativedelta(months=self.duration)
            month = len(str(date.month))
            if month < 2:
                month = "0"+ str(date.month)
            self.calibrated_due = str(date.year)+"-"+str(month)+"-"+str(date.day)

    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    instrument_no = fields.Char('Instrument Number')
    calibrated_on = fields.Date('Last Calibrated Date')
    duration = fields.Integer('Calibration Duration(Months)')
    calibrated_due = fields.Date('Next Calibration Due Date')
    status = fields.Selection([('calibrated', 'Calibrated'), ('not', 'Not Calibrated')], 'Status')
    location_id = fields.Many2one('stock.location', 'Availability')
