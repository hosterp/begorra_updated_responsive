from openerp.exceptions import Warning as UserError
from openerp import models, fields, api
from openerp.tools.translate import _


class bankBook(models.Model):
	_name = 'bank.book'
	_rec_name = 'date'
	_order = 'date desc'

	READONLY_STATES = {
		'close': [('readonly', True)],
	}

	@api.onchange('account_id')
	def onchange_account(self):
		if self.account_id and self.state in 'draft':
			balance = 0.0
			for b in self.env['account.account'].search([('parent_id','=',self.account_id.id)]):
				if b.type != 'view':
					balance += b.balance
				else:
					for bl in self.env['account.account'].search([('parent_id', '=', b.id)]):
						balance += bl.balance

			self.opening = balance


	@api.model
	def default_get(self, fields):
		res = super(bankBook, self).default_get(fields)
		line_id = self.env['bank.book.configuration.line'].search([('bankbook_config_id','=',self.env.user.company_id.id)], limit=1, order='id asc')
		if line_id:
			# return line_id.account_id.id
			res.update({'account_id': line_id.account_id.id})
		return res

	@api.multi
	@api.depends('move_lines')
	def compute_current_balance(self):
		for rec in self:
			debit = 0
			credit = 0
			for lines in rec.move_lines:
				debit += lines.debit
				credit += lines.credit
			rec.current_balance = abs((rec.opening + credit) - debit)

	@api.multi
	@api.depends('actual_balance')
	def compute_difference(self):
		if self.actual_balance:
			if self.actual_balance == self.current_balance:
				self.is_difference = False
			else:
				self.is_difference = True
				bank_book_config = self.env['res.company'].search([], limit=1)
				if bank_book_config:
					self.write_off_account = bank_book_config.write_off_account.id
		else:
			self.is_difference = False

	@api.onchange('individual_account_id')
	def onchange_individual_account_id(self):
		if self.individual_account_id:
			self.individual_account_balance = self.individual_account_id.balance

	@api.onchange('date')
	def onchange_date(self):
		if self.date:
			ids = []
			for b in self.env['account.account'].search([('parent_id', '=', self.account_id.id)]):
				if b.type != 'view':
					ids.append(b.id)
				else:
					for bl in self.env['account.account'].search([('parent_id', '=', b.id)]):
						ids.append(bl.id)
			return {'domain': {'individual_account_id': [('id', 'in', ids)]}}


	date = fields.Date('Date', states=READONLY_STATES)
	user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user, states=READONLY_STATES)
	individual_account_id = fields.Many2one('account.account', 'Individual Account', states=READONLY_STATES)
	individual_account_balance = fields.Float("Individual Account Balance")
	account_id = fields.Many2one('account.account', 'Account', states=READONLY_STATES)
	opening = fields.Float('Opening Balance')
	move_lines = fields.One2many('bank.book.line', 'bank_book_id', 'Transactions', states=READONLY_STATES)
	state = fields.Selection([('draft', 'Draft'),('open', 'Open'),('approve','Approve'),('reject','Locked'),('close', 'Closed')], 'State', default='draft')
	balance = fields.Float('Balance', states=READONLY_STATES)
	remarks = fields.Text('Remarks', states=READONLY_STATES)
	current_balance = fields.Float(compute='compute_current_balance', string="Balance")
	actual_balance = fields.Float('Actual Balance', states=READONLY_STATES)
	write_off_account =  fields.Many2one('account.account', 'Write Off Account', states=READONLY_STATES)
	is_difference = fields.Boolean(compute='compute_difference', string="Difference")
	company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)

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
			if rec.actual_balance != rec.current_balance:
				journal =  self.env['account.journal'].search([('type','=','general'),('company_id','=',rec.company_id.id)], limit=1)
				if not journal:
					raise UserError("Please create a journal with type 'General'.")					
				move = self.env['account.move'].create({'journal_id':journal.id,'date':rec.date})

				move_line = self.env['account.move.line']
				amount = 0
				debit_account = False
				credit_account = False
				if rec.actual_balance < rec.current_balance:
					amount = rec.current_balance - rec.actual_balance
					debit_account = rec.write_off_account.id
					credit_account = rec.account_id.id
				else:
					amount = rec.actual_balance - rec.current_balance
					debit_account = rec.account_id.id
					credit_account = rec.write_off_account.id
				move_line.create({'move_id':move.id,
								  'state': 'valid',
								  'name': 'Write Off amount from '+' '+rec.user_id.name+' on'+ str(rec.date),
								  'account_id':credit_account,
								  'debit':0,
								  'credit':amount,
								  'closed':True
								})
				move_line.create({'move_id':move.id,
								  'state': 'valid',
								  'name': 'Write Off amount from '+' '+rec.user_id.name+' on'+ str(rec.date),
								  'account_id':debit_account,
								  'debit':amount,
								  'credit':0,
								  'closed':True
								})
				for lines in rec.move_lines:
					if lines.closed == True:
						lines.bank_book_id = False
				move.button_validate()
				rec.state = 'close'
			else:
				rec.state = 'close'

	@api.model
	def create(self,vals):
		result = super(bankBook, self).create(vals)
		result.opening = result.account_id.balance
		return result

class SuspenseBookLine(models.Model):

	_name = 'bank.book.line'

	bank_book_id = fields.Many2one('bank.book', 'BankBook')
	narration = fields.Char('Description')
	account_id = fields.Many2one('account.account', 'Account')
	debit = fields.Float('Debit')
	credit = fields.Float('Credit')
	closed = fields.Boolean('Closed', default=False)
	move_id = fields.Many2one('account.move', 'Journal Entry')

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

class AccountMoveLine(models.Model):
	_inherit = 'account.move.line'

	bank_book_id = fields.Many2one('bank.book', 'Suspense Book')
	closed = fields.Boolean('Closed', default=False)

	@api.constrains('account_id')
	def _check_duplicate_account_id(self):
		if self.move_id.date:
			account_ids =  [line.account_id.id for line in self.company_id.accounts_ids]
			if self.account_id.id in account_ids:
				bank_book = self.env['bank.book'].search([('date','=',self.move_id.date),('account_id','=',account_ids[0]),('state','=','open')])
				if not bank_book:
					raise UserError("Please open today's Suspense Book...........!")

	@api.model
	def create(self,vals):
		result = super(AccountMoveLine, self).create(vals)
		if result.move_id.date:

			account_ids =  [line.account_id.id for line in result.company_id.accounts_ids]
			if result.account_id.parent_id.id in account_ids or result.account_id.parent_id.parent_id.id in account_ids:
				bank_book = self.env['bank.book'].search([('date','=',result.move_id.date),('account_id','=',account_ids[0]),('state','=','open')])
				if bank_book:
					if result.debit > 0.0:
						self.env['bank.book.line'].create({
							'bank_book_id': bank_book.id,
							'narration': result.name,
							'account_id': result.account_id.id,
							'move_id': result.move_id.id,
							'debit': 0.0,
							'credit': result.debit,
						})
					if result.credit > 0.0:
						self.env['bank.book.line'].create({
							'bank_book_id': bank_book.id,
							'narration': result.name,
							'account_id': result.account_id.id,
							'move_id': result.move_id.id,
							'debit': result.credit,
							'credit': 0.0,
						})
				else:
					raise UserError("Please open today's Suspense Book...........!")
		return result


class bankBookConfigurationLine(models.Model):
	_name = 'bank.book.configuration.line'

	bankbook_config_id = fields.Many2one('res.company', 'Suspense Book Configuration')
	account_id = fields.Many2one('account.account', "Account")



class ResCompany(models.Model):
	_inherit = 'res.company'

	accounts_ids = fields.One2many('bank.book.configuration.line', 'bankbook_config_id','Accounts To Book Register')
	write_off_account = fields.Many2one('account.account', 'Account for Write Off', domain=[('type','=','other')])

from openerp.osv import osv

class AccountMove(osv.osv):

	_inherit = 'account.move'

	def button_cancel(self, cr, uid, ids, context=None):
		for line in self.browse(cr, uid, ids, context=context):
			for ex in self.pool.get('bank.book.line').search(cr, uid, [('move_id', '=', line.id)]):
				if ex:
					self.pool.get('bank.book.line').browse(cr, uid, ex).unlink()
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





