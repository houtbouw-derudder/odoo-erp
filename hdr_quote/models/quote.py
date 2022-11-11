
from odoo import fields, models, api, _


class QuoteBlock(models.Model):
    _name = 'quote.block'
    _description = 'Quote'

    quote_id = fields.Many2one(comodel_name='quote', string="Quote", store=True)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='quote_id.currency_id')
    name = fields.Char(string="Name", copy=True, readonly=False, required=True)
    description = fields.Html(string="Description", copy=True, readonly=False, sanitize=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True)

    budget_materials = fields.Monetary(string='Budget materials', store=True)
    budget_equipments = fields.Monetary(string='Budget equipments', store=True)
    budget_production_hours = fields.Float(string='Budget production hours', store=True)
    budget_installation_hours = fields.Float(string='Budget installation hours', store=True)


class Quote(models.Model):
    _name = 'quote'
    _description = 'Quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('state')
    def _compute_name(self):
        for record in self:
            if record.state == "draft":
                record.name = "/"

    def _get_company_id(self):
        return self.env.company

    @api.depends('block_ids', 'block_ids.amount_untaxed')
    def _compute_amount(self):
        for record in self:
            amount_untaxed = 0
            for block in record.block_ids:
                amount_untaxed += block.amount_untaxed
            record.amount_untaxed = amount_untaxed
            record.amount_tax = 0.0
            record.amount_total = amount_untaxed + 0.0
            # calculate taxes and total

    def _get_move_display_name(self, show_ref=False):
        ''' Helper to get the display name of an invoice depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the journal entry reference.
        :return:            A string representing the invoice.
        '''
        self.ensure_one()
        name = ''
        if self.state == 'draft':
            name += {
                'quote': _('Draft Quote'),
                'estimate': _('Draft Estimate'),
            }[self.quote_type]
            name += ' '
        if not self.name or self.name == '/':
            name += '(* %s)' % str(self.id)
        else:
            name += self.name
        return name + (show_ref and self.ref and ' (%s%s)' % (self.ref[:50], '...' if len(self.ref) > 50 else '') or '')

    @api.depends('name', 'state')
    def name_get(self):
        result = []
        for move in self:
            name = move._get_move_display_name(show_ref=True)
            result.append((move.id, name))
        return result

    name = fields.Char(string='Number', copy=False, compute='_compute_name', readonly=False, store=True, index=True, tracking=True)
    date = fields.Date(string='Date', required=True, index=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False, tracking=True, default=fields.Date.context_today)
    ref = fields.Char(string='Reference', copy=False, tracking=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled'), ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    quote_type = fields.Selection(selection=[('quote', 'Quote'), ('estimate', 'Estimate')], string='Type', required=True, store=True, readonly=True, tracking=True, default='quote')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=_get_company_id)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')

    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, states={'draft': [(
        'readonly', False)]}, check_company=True, string='Partner', change_default=True, ondelete='restrict')
    # country_code = fields.Char(related='company_id.account_fiscal_country_id.code', readonly=True)
    # user_id = fields.Many2one(string='User', related='invoice_user_id', help='Technical field used to fit the generic behavior in mail templates.')

    introduction = fields.Html(string="Introduction", sanitize=True)
    conditions = fields.Html(string="Conditions", sanitize=True)

    block_ids = fields.One2many(comodel_name="quote.block", inverse_name="quote_id", string="Blocks", copy=True)

    # === Amount fields ===
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True, compute='_compute_amount')
    amount_tax = fields.Monetary(string='Tax', store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount')
