from openerp import fields, models, api
from datetime import date
from datetime import  datetime,timedelta
import json



class StockDashboard(models.Model):

    _name = 'stock.dashboard'

    def get_range(self):
        print "ffffffffffffffffffffff",json.dumps(range(3))
        return json.dumps(range(3))

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    department_list = fields.Text("Get Range",compute='get_range')


    
    