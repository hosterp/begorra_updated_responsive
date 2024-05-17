from openerp import models, fields, api

class WorkOrder(models.Model):
    _name = 'work.order.payment'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('sub.advance.payment') or '/'
        return super(WorkOrder, self).create(vals)
    @api.one
    def action_approve(self):
        self.state = 'approved'

    @api.one
    def action_reject(self):
        self.state = 'reject'

    @api.multi
    def action_advance(self):
        l = []
        for i in self.master_plan_line:
            l.append((0, 0, {
                'product_id': i.name.id,
                'qty': i.qty,
                'rate': i.rate,
                'sub_total': i.amt,
            })),
        sub_id = self.env['sub.advance.payment'].create({
            'partner_id': self.partner_id.id,
            'project_id': self.project_id.id,
            'work_order_no': self.id,
            'date_from': self.start_date,
            'date_to': self.end_date,
            'sub_bill_line': l,
        })
        self.advance_record = sub_id.id
        return {
            'name': 'Advance Payment',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sub.advance.payment',
            'target': 'new',
            'res_id': sub_id.id
        }

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_draft(self):
        self.state = 'draft'

    @api.one
    def action_start(self):
        self.state = 'start'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_paid(self):
        self.state = 'paid'


    @api.one
    def get_total(self):
        for s in self:
            total = 0.0
            for l in s.master_plan_line:
                total += l.amt
            s.amount_total = total

    name = fields.Char('Name', default="/")
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End `Date')
    project_id = fields.Many2one('project.project')
    partner_id = fields.Many2one('res.partner', 'Sub Contractor', domain="[('contractor', '=', True)]")
    mobile = fields.Char('Mobile')
    reference = fields.Text('Reference')
    company_id = fields.Many2one('res.company',"Company")
    state = fields.Selection([('draft', 'Waiting For Approval'),
                              ('approved', 'Approved'),
                              ('reject', 'Rejected'),
                              ('advance', 'Advance Paid'),
                              ('start', 'In Progress'),
                              ('done', 'Completed'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancelled')
                              ], 'Status', readonly=True, select=True, copy=False, default='draft')
    master_plan_line = fields.One2many('work.order.line.payment', 'line_id')
    amount_total = fields.Float('Total Amount', compute="get_total")
    advance_record = fields.Many2one('sub.advance.payment', string='Sub Contractor Advance')

class WorkOrderLinePayment(models.Model):
    _name = 'work.order.line.payment'

    @api.multi
    @api.depends('detailed_ids')
    def _get_total_qty(self):
        for value in self:
            qty = 0.0
            for val in value.detailed_ids:
                qty += val.qty

            value.qty = qty



    @api.one
    @api.depends('qty', 'rate')
    def _get_amt(self):
        if self.rate and self.qty:
            self.amt = self.rate * self.qty


    line_id = fields.Many2one('work.order.payment', string="Task")
    name = fields.Many2one('item.of.work', string="Item of Work")
    category = fields.Many2one('task.category', string="Category")
    qty = fields.Float(string="Quantity", compute='_get_total_qty')
    unit = fields.Many2one('product.uom', string="Unit")
    rate = fields.Float(string="Rate")
    amt = fields.Float(string="Amount", compute='_get_amt')
    note = fields.Text(string="Description")

    project_id = fields.Many2one(related='line_id.project_id', string='Project')
    detailed_ids = fields.One2many("detailed.workorder.line", 'detail_id', store=True)

class DetailedWorkOrderLine(models.Model):
    _name = "detailed.workorder.line"

    @api.one
    @api.depends('nos_x', 'length', 'breadth', 'depth')
    def _get_qty(self):
        self.qty = self.nos_x * self.length * self.breadth * self.depth



    detail_id = fields.Many2one('work.order.line.payment')
    date = fields.Date("Date")
    name = fields.Char(string="Description")
    side = fields.Selection([('r', 'RHS'), ('l', 'LHS'), ('bs', 'BS')], string="Side")
    chain_from = fields.Char('Chainage From')
    chain_to = fields.Char('Chainage To')
    nos_x = fields.Integer(string="Nos")
    length = fields.Float(string="L")

    breadth = fields.Float(string="W")

    depth = fields.Float(string="D")
    qty = fields.Float(string="Quantity", compute='_get_qty')
    qty_estimate = fields.Float('Qty As Per Budget Estimate')



