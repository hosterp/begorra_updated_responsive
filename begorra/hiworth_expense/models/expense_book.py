from openerp.exceptions import Warning as UserError
from openerp import models, fields, api
from openerp.tools.translate import _



class bankBook(models.Model):
    _name = 'expense.book'
    _rec_name = 'date'
    _order = 'date desc'

    READONLY_STATES = {
        'close': [('readonly', True)],
    }

    @api.multi
    @api.depends('move_lines')
    def compute_current_balance(self):
        for rec in self:
            debit = 0
            credit = 0
            re_debit = 0
            re_credit = 0
            for lines in rec.move_lines:
                debit += lines.debit
                credit += lines.credit
                if lines.state == 'reject':
                    re_debit += lines.debit
                    re_credit += lines.credit
            rec.current_balance = abs(debit - credit)
            rec.rejected = abs(re_debit - re_credit)
            rec.actual_balance = rec.current_balance - rec.rejected

    @api.multi
    @api.depends('actual_balance')
    def compute_difference(self):
            self.is_difference = False


    date = fields.Date('Date', states=READONLY_STATES)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, states=READONLY_STATES)
    move_lines = fields.One2many('expense.book.line', 'expense_book_id', 'Transactions', states=READONLY_STATES)
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Open'),
                              ('approve','Approve'),
                              ('reject','Locked'),
                              ('close', 'Closed'),
                              ('cancel','Cancelled')], 'State', default='draft')
    remarks = fields.Text('Remarks', states=READONLY_STATES)
    current_balance = fields.Float(compute='compute_current_balance', string="Balance")
    actual_balance = fields.Float('Actual Balance', states=READONLY_STATES,compute='compute_current_balance',)
    write_off_account =  fields.Many2one('account.account', 'Write Off Account', states=READONLY_STATES)
    is_difference = fields.Boolean(compute='compute_difference', string="Difference")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    rejected = fields.Float('Rejected Balance',compute='compute_current_balance',)

    @api.multi
    def action_open(self):
        for rec in self:
            rec.state = 'open'
    
    @api.multi
    def action_approve(self):
        for rec in self:
            rec.state = 'approve'
    
    @api.multi
    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    @api.multi
    def action_close(self):
        for rec in self:
            rec.state = 'close'

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'

class AcccountMove(models.Model):

    _inherit = "account.move"

    copy_to_expense = fields.Boolean('View In Expense')

from openerp.osv import osv

class AccountMove(osv.osv):

    _inherit = 'account.move'

    def button_cancel(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            for ex in self.pool.get('expense.book.line').search(cr, uid, [('move_id', '=', line.id)]):
                if ex:
                    self.pool.get('expense.book.line').browse(cr, uid, ex).unlink()
            cr.execute('UPDATE account_move_line ' \
                       'SET is_posted=False ' \
                       'WHERE move_id = %s',
                       (line.id,))
            if not line.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _(
                    'You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if ids:
            cr.execute('UPDATE account_move ' \
                       'SET state=%s ' \
                       'WHERE id IN %s', ('draft', tuple(ids),))

            self.invalidate_cache(cr, uid, context=context)
        return True

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def create(self, vals):
        result = super(AccountMoveLine, self).create(vals)
        if result.move_id.date:
            if result.move_id.copy_to_expense and result.move_id.journal_id.name == 'Site':
                account_ids = [line.account_id.id for line in result.company_id.accounts_ids]
                if result.account_id.parent_id.id not in account_ids and result.account_id.parent_id.parent_id.id not in account_ids:
                    expense_book = self.env['expense.book'].search([('date', '=', result.move_id.date), ('state', '=', 'open')])
                    if expense_book:
                        if result.debit > 0.0:
                            self.env['expense.book.line'].create({
                                'expense_book_id': expense_book.id,
                                'narration': result.name,
                                'account_id': result.account_id.id,
                                'move_id': result.move_id.id,
                                'statement_id': result.move_id.partner_stmt_id.id,
                                'debit': 0.0,
                                'credit': result.debit,
                            })
                        if result.credit > 0.0:
                            self.env['expense.book.line'].create({
                                'expense_book_id': expense_book.id,
                                'narration': result.name,
                                'statement_id': result.move_id.partner_stmt_id.id,
                                'account_id': result.account_id.id,
                                'move_id': result.move_id.id,
                                'debit': result.credit,
                                'credit': 0.0,
                            })
                    else:
                        raise UserError("Please open today's Expense Book...........!")
        return result

class ExpenseBookLines(models.Model):

    _name = "expense.book.line"
    _order = "move_id"

    expense_book_id = fields.Many2one('expense.book', 'CashBook')
    narration = fields.Char('Description')
    date = fields.Date('Date')
    statement_id = fields.Many2one('partner.daily.statement')
    dds_id = fields.Many2one('driver.daily.statement')
    account_id = fields.Many2one('account.account', 'Account')
    debit = fields.Float('Debit')
    credit = fields.Float('Credit')
    closed = fields.Boolean('Closed', default=False)
    move_id = fields.Many2one('account.move', 'Journal Entry')
    location_ids = fields.Many2one('stock.location', 'Site', domain=[('usage', '=', 'internal')])
    state = fields.Selection([('draft','Draft'),
                              ('approve','Approved'),
                              ('reject','Rejected'),
                              ('cancel','Cancelled')],default='draft')


    def open_line_transactions(self, cr,uid,ids,args=None):
        obj = ''
        for s in self.browse(cr,uid,ids):
            obj = s
        return {
            'name': _('Transaction History'),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('account_id', '=', obj.account_id.id)],
        }
        
    @api.multi
    def action_approve(self):
        for rec in self:
            if rec.move_id and rec.move_id.state == 'draft':
                rec.move_id.button_validate()
            rec.state = 'approve'
    
    @api.multi
    def action_reject(self):
        for rec in self:
            rec.state = 'reject'

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            


