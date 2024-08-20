from openerp import fields, models, api

class ExpenseExpense(models.Model):
    _name = 'expense.expense'
    
    @api.depends('expense_line_ids')
    def compute_amount(self):
        for rec in self:
            total = 0
            for expense in rec.expense_line_ids:
                total +=expense.amount
            rec.amount_total = total
            
            
    date = fields.Date('Date', default=fields.datetime.now())
    state = fields.Selection([('draft','Draft'),('posted','Posted')],default='draft', string="State")
    journal_id = fields.Many2one('account.journal',string="Journal", copy=False)
    move_id = fields.Many2one('account.move',string="Journal Entry",copy=False)
    expense_line_ids = fields.One2many('expense.line','expense_id',string="Expense Line")
    from_readonly = fields.Boolean('Readonly')
    amount_total = fields.Float(string="Total",compute='compute_amount')
    journal_type = fields.Selection([('sale','Sale'),('sale_refund','Sale Refund'),
                                     ('purchase','Purchase'),('cash','Cash'),
                                     ('bank','Banks and Checks'),('general','General'),
                                     ('situation','Opening/Closing Situation')], string="Journal Type")

    @api.onchange('journal_id')
    def onchange_journal(self):
        # self.journal_type = self.journal_id.type
        if self.journal_id.name == 'Site':
            self.from_readonly = False
        else:
            self.from_readonly = True

    @api.multi
    def action_post(self):
        move_obj = self.pool.get('account.move')
        move_line_obj = self.pool.get('account.move.line')
        user_obj = self.pool.get('res.users')
        move_vals = {}
        if self.journal_id.name != 'Site':
            for i in self.expense_line_ids:
                i.from_account_id = self.journal_id.default_credit_account_id.id
      
      
        for expense in self:
            if not expense.move_id:
                move_vals = {'journal_id': expense.journal_id.id,
                        'company_id': self.env.user.company_id.id,
                        'date':expense.date
                        }
                if self.journal_id.name == 'Site':
                    move_vals.update({'copy_to_expense':True})
                move_line_list = []
                for expense_line in expense.expense_line_ids:
                    move_line_list.append((0,0,{'name': expense_line.narration,
                                            'account_id': expense_line.to_account_id.id,
                                            'debit': expense_line.amount,
                                            'credit': 0,
                                            }))

                    move_line_list.append((0,0,{'name': expense_line.narration,
                                            'account_id': expense_line.from_account_id.id,
                                            'debit': 0,
                                            'credit': expense_line.amount}))
                    
                move_vals.update({'line_id':move_line_list})
                move_id = move_obj.create(self.env.cr, self.env.uid, move_vals, context=None)
                move_obj.browse(self.env.cr, self.env.uid,move_id,context=None).button_validate()
                for expense_line in expense.expense_line_ids:
                    if expense_line.to_account_id.name == 'CASH IN BOX':
                        cash_book = self.env['cash.book'].search(
                            [('date', '=', expense.date), ('state', '=', 'open')])
                        if expense_line.amount > 0.0:
                            self.env['cash.book.line'].create({
                                'cash_book_id': cash_book.id,
                                'narration': "Bank Withdrawal",
                                # 'statement_id': self.id,
                                'account_id': expense_line.from_account_id.id,
                                'debit': expense_line.amount,
                                # 'date': self.date,
                                # 'location_ids': self.location_ids.id,
                                'move_id':move_id,
                                'credit': 0.0,
                            })
                expense.write({'move_id': move_id, 'state': 'posted'})


class ExpenseLine(models.Model):
    _name = 'expense.line'

    from_readonly = fields.Boolean('Readonly')
    expense_id = fields.Many2one('expense.expense', string="Expense")
    from_account_id = fields.Many2one('account.account', string="From Account", domain="[('type', '!=', 'view')]")
    to_account_id = fields.Many2one('account.account', string="To Account", domain="[('type', '!=', 'view')]")
    narration = fields.Char(string="Narration")
    amount = fields.Float(string="Amount")
