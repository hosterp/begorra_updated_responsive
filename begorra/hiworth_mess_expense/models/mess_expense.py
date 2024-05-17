from openerp import models, fields, api, _

class MessExpense(models.Model):
    _name = 'mess.expense'

    
            
            
    @api.model
    def create(self, vals):
        vals.update({'name': self.env['ir.sequence'].next_by_code('mess.expense.code')})
        res = super(MessExpense, self).create(vals)
        
        return res
        
    @api.depends('total_man_power','total_provision','total_vegetables','total_milk_curd',
                 'purchase_packing_material','total_non_veg_purchase','total_gas_cylinder','miscellaneous')
    def compute_total(self):
        for rec in self:
            attendance = self.env['mess.attendance'].search([('date','=',rec.date),('attendance','!=','absent')])
            if attendance:
                rec.total_man_power = len(attendance.ids)
            else:
                rec.total_man_power = 0
            rec.total_provision = rec.provision
            veg_total = 0
            for veg in rec.vegetables_expense_ids:
                veg_total += veg.total
            rec.total_vegetables = veg_total
            non_veg_total = 0
            for non_veg in rec.non_vegetables_expense_ids:
                non_veg_total += non_veg.total
            rec.total_non_veg_purchase = non_veg_total
            for particular in rec.particular_expense_ids:
                rec.total_milk_curd = particular.milk_amt + particular.milk_amt
                rec.total_gas_cylinder = particular.gas_no
            
            rec.purchase_packing_material = rec.packing_expense
            rec.miscellaneous = rec.miscellaneous_amount
            rec.total_stock = rec.total_man_power + rec.total_provision + rec.total_vegetables + rec.total_non_veg_purchase \
                                +  rec.total_gas_cylinder + rec.total_milk_curd + rec.purchase_packing_material + rec.miscellaneous
            
    
    name = fields.Char(string="Name")
    date = fields.Date(string="Date",default=fields.date.today())
    provision = fields.Integer(string="Provision")
    
    vegetables_expense_ids = fields.One2many('vegetables.expense','mess_expense_id', string="Vegetables")
    particular_expense_ids = fields.One2many('particulars.expense', 'mess_expense_id', string="Particulars")
    packing_expense = fields.Float(string="Packing Expense")
    
    non_vegetables_expense_ids = fields.One2many('non.vegetables.expense','mess_expense_id', string="Non Vegetables")
    miscellaneous_amount = fields.Float(string="Miscellaneous Amount")
    
    total_man_power = fields.Float(string="Man Power",compute='compute_total')
    total_provision = fields.Float(string="Total Provision Purchase", compute='compute_total')
    total_vegetables = fields.Float(string="Total Vegetables Purchase", compute='compute_total')
    total_milk_curd = fields.Float(string="Total Milk/Curd", compute='compute_total')
    purchase_packing_material = fields.Float(string="Purchase Picking Material for Parcel", compute='compute_total')
    total_non_veg_purchase = fields.Float(string="Total Non-Veg purchase (Chicken,Fish,Meet&Egg)", compute='compute_total')
    total_gas_cylinder = fields.Float(string="Total Gas Cylinder Purchase",compute='compute_total')
    miscellaneous = fields.Float(string="Miscellaneous",compute='compute_total')
    opening_stock = fields.Float(string="Opening Stock")
    total_stock = fields.Float(string="Total Stock",compute='compute_total')
    project_id = fields.Many2one('project.project',string="Project")
    guest = fields.Float(string="Guest")
    attendance_ids = fields.One2many('mess.report.attendance','mess_expense_id',string="Mess Staff Attendance")
    
    
    @api.multi
    def load_employee_mess_attendance(self):
        return {
           'name':'Mess Attendance',
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'type': 'ir.actions.act_window',
            "views": [
                [self.env.ref("hiworth_mess_expense.hr_employee_view_mess_expense").id, "tree"],
                [False, "form"]],
            'domain': [],
            "context": {}
        }
    
    
class VegetablesExpense(models.Model):
    _name = 'vegetables.expense'
    
    
    @api.depends('product_qty','rate')
    def compute_total(self):
        for rec in self:
            rec.total = rec.product_qty * rec.rate
            
    product_id = fields.Many2one('product.product', string="Products")
    product_qty = fields.Float(string="Quantity")
    rate = fields.Float(string="Rate")
    total = fields.Float(compute='compute_total',string="Total")
    mess_expense_id = fields.Many2one('mess.expense',string="Mess Expense")


class NonVegetablesExpense(models.Model):
    _name = 'non.vegetables.expense'
    
    @api.depends('product_qty', 'rate')
    def compute_total(self):
        for rec in self:
            rec.total = rec.product_qty * rec.rate
    
    product_id = fields.Many2one('product.product', string="Products")
    product_qty = fields.Float(string="Quantity")
    rate = fields.Float(string="Rate")
    total = fields.Float(compute='compute_total', string="Total")
    mess_expense_id = fields.Many2one('mess.expense', string="Mess Expense")
    
class ParticularsExpense(models.Model):
    _name = 'particulars.expense'

    @api.depends('gas_no', 'gas_rate')
    def compute_gas_total(self):
        for rec in self:
            rec.gas_total = rec.gas_no * rec.gas_rate

    @api.depends('milk', 'milk_rate')
    def compute_milk_total(self):
        for rec in self:
            rec.milk_amt = rec.milk * rec.milk_rate

    @api.depends('curd', 'curd_rate')
    def compute_curd_total(self):
        for rec in self:
            rec.curd_amt = rec.curd * rec.curd_rate

    @api.depends('cooking_water', 'cooking_water_rate')
    def compute_cooking_total(self):
        for rec in self:
            rec.cooking_water_amt = rec.cooking_water * rec.cooking_water_rate
            
    milk = fields.Float(string="Milk (Packets/Litre)")
    milk_rate = fields.Float(string="Milk Rate")
    milk_amt = fields.Float(string="Milk/Curd Amount", compute='compute_milk_total')
    curd = fields.Float(string="Curd")
    curd_rate = fields.Float(string="Curd Rate")
    curd_amt = fields.Float(string="Curd Amount", compute='compute_curd_total')
    cooking_water = fields.Float(string="Cooking Water (Litre)")
    cooking_water_rate = fields.Float(string="Rate")
    cooking_water_amt = fields.Float(string="Amount", compute='compute_cooking_total')
    gas_no = fields.Float(string="No of Gas cylinder")
    gas_rate = fields.Float(string="Rate")
    gas_total = fields.Float(string="Amount", compute='compute_gas_total')
    mess_expense_id = fields.Many2one('mess.expense', string="Mess Expense")
    