from openerp import models, fields, api, _
from openerp.osv import osv

class MasterDataEstimation(models.Model):
    _name = 'master.data.estimation'
    _rec_name = 'item_work_id'
    
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        for rec in self:
            rec.name = rec.product_id.name

    @api.onchange('product_id')
    def onchange_category_id(self):
        # item = []
        # cate = []
        for rec in self:
            if rec.product_id:
                for line in rec.project_id.task_ids:
                    for task_line in line.task_line:
                        if rec.product_id == task_line.category:
                            rec.item_work_id = task_line.name.id

            
        #     for line in project.task_ids:
        #          for task_line in line.task_line:
        #             item.append(task_line.name.id)
        #             cate.append(task_line.category.id)
        # return {'domain':{'item_work_id':[('id','in',item)],
        #                    'category_id':[('id','in',cate)]}}
            
    @api.model
    def create(self, vals):
        if vals.get('name',False):
            self.check_name(vals.get('item_work_id'))
        res = super(MasterDataEstimation, self).create(vals)
        return res
    
    @api.multi
    def write(self,vals):
        res = super(MasterDataEstimation, self).write(vals)
        if res:
            self.check_name(self.item_work_id.id)
        return res
    
    def check_name(self,name):
        estimation_ids = self.search([('item_work_id','=',name)])
        if estimation_ids:
            raise osv.except_osv(_('Warning!'),("Estimation already exists"))
        
    @api.depends('labour_wage','no_of_labours')
    def compute_cost(self):
        for rec in self:
            rec.total_amount = rec.no_of_labours * rec.labour_wage
        
    product_id = fields.Many2one('task.category',string="Category")
    item_work_id = fields.Many2one('item.of.work',string="Item of work")
    project_id = fields.Many2one('project.project',string="Project")
    no_of_labours = fields.Float(string="No of Labours")
    no_of_machines = fields.Float(string="NO of Machines")
    veh_categ_id = fields.Many2many('vehicle.category.type', string='Machinery')
    labour_wage = fields.Float(string="Labour Wage")
    total_amount = fields.Float(string="Cost",compute = 'compute_cost')