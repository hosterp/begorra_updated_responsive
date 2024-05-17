from openerp import fields, models, api
import datetime

class Mou(models.Model):
    _name = 'mou.mou'

    @api.model
    def create(self, vals):
       if vals.get('name', '/') == '/':
           vals['name'] = self.env['ir.sequence'].get('mou.sequence')+'/'+str(datetime.datetime.now().date().year) or '/'
        
       return super(Mou, self).create(vals)
   
   
    @api.onchange('partner_id')
    def onchange_partner_id(self):
        address_list = []
        for mou in self:
            if mou.partner_id:
                if mou.partner_id.street:
                    address_list.append(mou.partner_id.street)
                if mou.partner_id.street2:
                    address_list.append(mou.partner_id.street2)
                if mou.partner_id.city:
                    address_list.append(mou.partner_id.city)
                if mou.partner_id.state_id:
                    address_list.append(mou.partner_id.state_id.name)
                if mou.partner_id.country_id:
                    address_list.append(mou.partner_id.country_id.name)
                if mou.partner_id.mobile:
                    address_list.append(mou.partner_id.mobile)
            address = ','.join(address_list)
            mou.address = address
#             return {'value':{'address':address}}


    @api.depends('cost','bata')
    def compute_total(self):
        for record in self:
           record.total = record.cost + record.bata
    
    name = fields.Char(string="MOU No.", copy=False)
    partner_id = fields.Many2one('res.partner', string="Name of Supplier/Owner", required=True, domain="['|','|',('other_mou_supplier','=', True),('veh_owner','=', True), ('is_rent_mach_owner','=', True)]")
    address = fields.Text(string="Address")
    agreement_date = fields.Date(string="Agreement Date", required=True)
    cost = fields.Float(string="Agreement Cost", required=True)
    unit_of_meassure = fields.Many2one('mou.unit', 'Payment Unit', required=True)
    bata = fields.Float(string="Bata")
    starting_date = fields.Date(string="Starting Date", required=True)
    finishing_date = fields.Date(string="Finishing Date")
    amount = fields.Float(string="Amount")
    mode_of_payment = fields.Selection([('bank', 'Bank'), ('cash', 'Cash')], string="Mode of Payment")
    date_of_payment = fields.Date(string="Date of Payment")
    pan = fields.Char(string="PAN")
    gst_account= fields.Char(string="GST Account Name")
    gst_no = fields.Char(string="GST No.")
    account_name = fields.Char(string="Account Name")
    bank_name = fields.Char(string="Bank Name")
    branch = fields.Char(string="Branch")
    acc_no = fields.Char(string="A/C No.")
    ifsc_code = fields.Char(string="IFSC Code")
    site = fields.Many2one('stock.location', 'Site', required=True)
    supervisor = fields.Many2one('hr.employee', string="Supervisor", domain="[('user_category', 'in', ['supervisor','admin','interlocks','cheif_acc','sen_acc','jun_acc'])]", required=True)
    category_id = fields.Many2one('mou.category', string="Category", required=True)
    contractor_id = fields.Many2one('res.partner', string="Contractor")
    type = fields.Many2one('vehicle.category.type', 'Vehicle Type', related='vehicle_number.vehicle_categ_id')
    vehicle_number = fields.Many2many('fleet.vehicle', string="Vehicle", domain="['|',('is_rent_mach', '=', True), ('rent_vehicle', '=', True)]")
    land_area = fields.Char(string="Land Area")
    with_operator = fields.Boolean(string="With Operator")
    total = fields.Float(string="Total", compute='compute_total', store=True)
    company_id = fields.Many2one('res.company', string="Company")
    state = fields.Selection([('draft','Draft'), ('approved', 'Approved'), ('rejected', 'Rejected')],default="draft", string="Status")
    
    
    _defaults = {
        'name': lambda obj, cr, uid, context: '/',
    }
    
    
    @api.multi
    def action_approve(self):
        for mou in self:
            mou.write({'state': 'approved'})
            
    @api.multi
    def action_reject(self):
        for mou in self:
            mou.write({'state':'rejected'})
            
            
class MouCategory(models.Model):
    _name = 'mou.category'
    _rec_name = "name"

    name = fields.Char(string="Name")  

class MouUnit(models.Model):

    _name = "mou.unit"
    _rec_name = "name"

    name = fields.Char('Name')
    code = fields.Char('Code')

class ResPartner(models.Model):

    _inherit = "res.partner"

    other_mou_supplier = fields.Boolean('Other MOU Supplier/Owner')

    @api.multi
    def action_show_mou(self):

        view_tree = self.env.ref('expense_voucher.view_mou_tree')
        view_form = self.env.ref('expense_voucher.view_mou_form')
        return {
            'name': 'Related MOU Details',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mou.mou',
            'views': [(view_tree.id, 'tree'), (view_form.id, 'form')],
            'target': 'current',
            'domain': [('partner_id', '=', self.id)],
        }