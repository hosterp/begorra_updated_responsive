from openerp import fields, models, api

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    
    mou_id = fields.Many2one('fleet.vehicle', string="MOU")