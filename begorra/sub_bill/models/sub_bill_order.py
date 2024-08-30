from openerp import models, fields, api

class SubAdvancePayment(models.Model):

    _name = 'sub.advance.payment'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('sub.advance.payment') or '/'
        return super(SubAdvancePayment, self).create(vals)

    @api.one
    def get_total(self):
        for s in self:
            total = 0.0
            for l in s.sub_bill_line:
                total += l.sub_total
            s.amount_total = total

    @api.one
    @api.depends('amount_total_paid', 'amount_total')
    def get_total_diff(self):
        for s in self:
            s.amount_difference = s.amount_total - s.amount_total_paid

    @api.onchange('advance_percentage')
    @api.depends('amount_total')
    def onchange_advance_percentage(self):
        if self.advance_percentage:
            self.amount_total_paid = (self.advance_percentage/100) * self.amount_total

    @api.one
    def button_verify(self):
        self.state = 'verified'
        self.cked_verified_by = self.env.user.id
    @api.one
    def button_approve(self):
        self.state = 'approved'
        self.approved_by = self.env.user.id

    @api.one
    def button_pay(self):
        self.state = 'paid'
        self.work_order_no.state = 'advance'
        
        
    @api.onchange('work_order_no')
    def onchange_work_order_no(self):
        for rec in self:
            vals_dict = []
            for plan in rec.work_order_no.master_plan_line:
                if plan.date >=rec.date_from and plan.date<=rec.date_to:
                    vals={'product_id': plan.name.id,
                    'qty':plan.qty,
                    'rate':plan.rate,}
                    vals_dict.append((0,0,vals))
            rec.sub_bill_line = vals_dict
        

    name = fields.Char('Code', default="/")
    partner_id = fields.Many2one('res.partner', 'Sub Contractor', domain="[('contractor', '=', True)]")
    project_id = fields.Many2one('project.project', 'Work/ Project')
    work_order_no = fields.Many2one('work.order.payment', 'Work Order')
    date_from = fields.Date('Period From')
    date_to = fields.Date('Period To')
    sub_bill_line = fields.One2many('sub.advance.line', 'sub_id')
    cked_verified_by = fields.Many2one('res.users', 'Checked And Verified By')
    approved_by = fields.Many2one('res.users', 'Approved By')
    state = fields.Selection([('draft', 'Draft'), ('verified', 'Verified'), ('approved', 'Approved'), ('paid', 'Paid')], default='draft')
    amount_total = fields.Float('Total Amount', compute="get_total")
    advance_percentage = fields.Float('Advance Percentage')
    amount_total_paid = fields.Float('Advance Paid')
    amount_difference = fields.Float('Difference Amount', compute="get_total_diff")

class SubContractorWorkOrderLine(models.Model):

    _name = 'sub.advance.line'

    @api.one
    def get_total(self):
        for s in self:
            s.sub_total = s.qty * s.rate

    date = fields.Date("Date", default=lambda self: fields.datetime.now())
    sub_id = fields.Many2one('sub.advance.payment')
    product_id = fields.Many2one('item.of.work', 'Item Description')
    qty = fields.Float('Quantity')
    rate = fields.Float('Rate')
    sub_total = fields.Float('Amount', compute="get_total")
    remarks = fields.Char('Remarks')

class ProjectInherit(models.Model):

    _inherit = "project.project"

    subcontractor_advances = fields.One2many('sub.advance.payment', 'project_id', string="Advances")