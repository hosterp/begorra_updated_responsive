from openerp import models, fields, api, _


class MasterPlan(models.Model):
    _name = 'master.plan'

    @api.one
    @api.depends('nos', 'length', 'breadth', 'depth')
    def _get_qty(self):
        for rec in self:
            rec.qty = rec.nos * rec.length * rec.breadth * rec.depth

    category_id = fields.Many2one('task.category', "Category")
    name = fields.Char("Item Description")
    chain_from = fields.Char('Chainage From')
    chain_to = fields.Char('Chainage To')
    side = fields.Selection([('r', 'RHS'), ('l', 'LHS'), ('bs', 'BS')], string="Side")
    unit_id = fields.Many2one('product.uom', "Unit")
    nos = fields.Float("Nos", default=1)
    length = fields.Float(string="Length(m)", default=1)
    breadth = fields.Float(string="Breadth(m)", default=1)
    depth = fields.Float(string="Depth(m)", default=1)
    qty = fields.Float(string="Qty(cum)", compute='_get_qty')
    contractor_id = fields.Many2one('res.partner', domain=[('contractor', '=', True)], string="Contractor")
    remarks = fields.Char("Remarks")
    statement_id = fields.Many2one('partner.daily.statement',"statement")

class MasterPlanManPower(models.Model):
    _name = 'master.plan.manpower'

    skilled_avail = fields.Float("Skilled Available")
    skilled_required = fields.Float("Skilled Required")
    unskilled_avail = fields.Float("Unskilled Available")
    unskilled_requi = fields.Float("Unskilled Required")
    semi_avail =fields.Float("SemiSkilled Available")
    semi_require = fields.Float("SemiSkilled Required")
    statement_id = fields.Many2one('partner.daily.statement', "statement")

class MasterPlanMachinery(models.Model):
    _name = 'master.plan.machinery'

    machinery_id = fields.Many2one('fleet.vehicle',"Machinery")
    available = fields.Float("Available")
    required = fields.Float("Required")
    statement_id = fields.Many2one('partner.daily.statement', "statement")


class MasterPlanMaterial(models.Model):
    _name = 'master.plan.material'

    material_id = fields.Many2one('product.product',"Material")
    available = fields.Float("Available")
    required = fields.Float("Required")
    statement_id = fields.Many2one('partner.daily.statement', "statement")

class PartnerDailyStatement(models.Model):
    _inherit = 'partner.daily.statement'

    next_day_planning = fields.One2many('master.plan', 'statement_id', string="Next Day Planning")
    next_day_manpower = fields.One2many('master.plan.manpower', 'statement_id', string="Next Day Planning")
    next_day_machinery = fields.One2many('master.plan.machinery', 'statement_id', string="Next Day Planning")
    next_day_material = fields.One2many('master.plan.material', 'statement_id', string="Next Day Planning")