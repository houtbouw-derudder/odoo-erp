
import logging

from json import dumps

from odoo import fields, models, api, Command, _


class QuoteBlock(models.Model):
    _name = 'quote.block'
    _description = 'Quote'

    quote_id = fields.Many2one(comodel_name='quote', string="Quote", store=True)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='quote_id.currency_id')
    name = fields.Char(string="Name", copy=True, readonly=False, required=True)
    description = fields.Html(string="Description",copy=True, readonly=False, sanitize=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True)

    budget_materials = fields.Monetary(string='Budget materials', store=True)
    budget_equipments = fields.Monetary(string='Budget equipments', store=True)
    budget_production_hours = fields.Float(string='Budget production hours', store=True)
    budget_installation_hours = fields.Float(string='Budget installation hours', store=True)


class Quote(models.Model):
    _name = 'quote'
    _description = 'Quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_quote_display_name(self, show_ref=False):
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

    def _get_company_id(self):
        return self.env.company

    def _get_default_tax_ids(self):
        return [t.id for t in self.env.company.account_sale_tax_id]

    @api.depends('state')
    def _compute_name(self):
        for record in self:
            if record.state == "draft":
                record.name = "/"

    @api.depends('name', 'state')
    def name_get(self):
        result = []
        for move in self:
            name = move._get_quote_display_name(show_ref=True)
            result.append((move.id, name))
        return result        

    @api.onchange('partner_id')
    def _onchange_partner(self):
        for record in self:
            record.fiscal_position_id = self.env['account.fiscal.position'].get_fiscal_position(record.partner_id.id)

    @api.depends('company_id', 'fiscal_position_id')
    def _compute_tax_ids(self):
        for record in self:
            logging.warning("%s", record)
            tax_ids = record.company_id.account_sale_tax_id
            if record.fiscal_position_id:
                tax_ids = record.fiscal_position_id.map_tax(tax_ids)

            logging.warning("set tax_ids: %s", tax_ids)
            record.tax_ids = tax_ids

    @api.depends('block_ids', 'block_ids.amount_untaxed', 'tax_ids')
    def _compute_totals(self):
        logging.warning("_compute_totals")
        for record in self:
            if not record.block_ids:
                record.amount_untaxed = 0.0
                record.tax_totals = None
                record.amount_total = 0.0
            else:
                amount_untaxed = 0.0
                for block in record.block_ids:
                    amount_untaxed += block.amount_untaxed

                tax_calc = record.tax_ids.compute_all(amount_untaxed, currency=record.currency_id, partner=record.partner_id)

                record.amount_untaxed = tax_calc["total_void"]
                record.tax_totals = None
                record.amount_total = tax_calc["total_included"]

    name = fields.Char(string='Number', copy=False, compute='_compute_name', readonly=False, store=True, index=True, tracking=True)
    date = fields.Date(string='Date', required=True, index=True, readonly=True, states={'draft': [('readonly', False)]}, copy=False, tracking=True, default=fields.Date.context_today)
    ref = fields.Char(string='Reference', copy=False, tracking=True)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled'), ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    quote_type = fields.Selection(selection=[('quote', 'Quote'), ('estimate', 'Estimate')], string='Type', required=True, store=True, readonly=True, tracking=True, default='quote')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=_get_company_id)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
    tax_ids = fields.Many2many(comodel_name='account.tax', string="Taxes", compute="_compute_tax_ids")
    
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, states={'draft': [('readonly', False)]}, check_company=True, string='Partner', change_default=True, ondelete='restrict')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="[('company_id', '=', company_id)]", ondelete="restrict")

    introduction = fields.Html(string="Introduction", sanitize=True)
    conditions = fields.Html(string="Conditions", sanitize=True)

    block_ids = fields.One2many(comodel_name="quote.block", inverse_name="quote_id", string="Blocks", copy=True)

    # === Amount fields ===
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_compute_totals')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    tax_totals = fields.Char(string="Tax Totals", store=True, readonly=False)
