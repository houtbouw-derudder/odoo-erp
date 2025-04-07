
import logging
from collections import defaultdict
from json import dumps, loads

from odoo import fields, models, api, Command, _
from odoo.exceptions import UserError, AccessError
from odoo.tools import float_compare
from odoo.tools.misc import formatLang

QUOTE_NUMBER_SEQUENCE_CODE = 'quote.number'

class QuoteBlock(models.Model):
    _name = 'quote.block'
    _description = 'Quote'

    quote_id = fields.Many2one(comodel_name='quote', string="Quote", store=True)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='quote_id.currency_id')
    name = fields.Char(string="Name", copy=True, readonly=False, required=True)
    sequence = fields.Integer(default=10)
    description = fields.Html(string="Description",copy=True, readonly=False, sanitize=True)
    notes = fields.Html(string="Internal notes", copy=True, readonly=False, sanitize=True)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True)

    budget_materials = fields.Monetary(string='Budget materials', store=True)
    budget_equipments = fields.Monetary(string='Budget equipments', store=True)
    budget_production_hours = fields.Float(string='Budget production hours', store=True)
    budget_installation_hours = fields.Float(string='Budget installation hours', store=True)

    def _prepare_base_line_for_taxes_computation(self, **kwargs):
        """ Convert the current record to a dictionary in order to use the generic taxes computation method
        defined on account.tax.

        :return: A python dictionary.
        """
        self.ensure_one()
        return self.env['account.tax']._prepare_base_line_for_taxes_computation(
            self,
            **{
                'tax_ids': self.quote_id.tax_id,
                'quantity': 1.0,
                'partner_id': self.quote_id.partner_id,
                'currency_id': self.quote_id.currency_id or self.quote_id.company_id.currency_id,
                'rate': self.quote_id.currency_rate,
                'price_unit': self.amount_untaxed,
                **kwargs,
            },
        )


class Quote(models.Model):
    _name = 'quote'
    _description = 'Quote'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_quote_display_name(self, show_ref=False):
        ''' Helper to get the display name of a quote depending of its type.
        :param show_ref:    A flag indicating of the display name must include or not the reference.
        :return:            A string representing the quote.
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
            if record.state == "posted" and record.name == '/':
                record.name = self.env['ir.sequence'].with_context(sequence_date=record.date).next_by_code(QUOTE_NUMBER_SEQUENCE_CODE)


    @api.depends('name', 'state')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record._get_quote_display_name(show_ref=True)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        for record in self:
            record.fiscal_position_id = self.env['account.fiscal.position']._get_fiscal_position(record.partner_id)
            record.payment_term_id = record.partner_id.property_payment_term_id or record.payment_term_id

    @api.depends('company_id', 'fiscal_position_id', 'tax_ids')
    def _compute_tax_ids(self):
        for record in self:
            tax_ids = record.tax_ids or record.company_id.account_sale_tax_id
            if record.fiscal_position_id:
                tax_ids = record.fiscal_position_id.map_tax(tax_ids)
            record.tax_ids = tax_ids

    @api.depends('date', 'payment_term_id')
    def _compute_date_due(self):
        for record in self:
            if record.payment_term_id and record.date:
                terms = record.payment_term_id._compute_terms(
                    date_ref=record.date,
                    currency=self.env.company.currency_id,
                    company=self.env.company,
                    tax_amount=1,
                    tax_amount_currency=1,
                    untaxed_amount=1,
                    untaxed_amount_currency=1,
                    sign=1)
                
                terms = sorted(terms['line_ids'], key=lambda r: r.get("date"), reverse=True)                
                record.date_due = terms[0].get('date', record.date) if len(terms) > 0 else record.date
            else:
                record.date_due = record.date

    name = fields.Char(string='Number', copy=False, compute='_compute_name', readonly=False, store=True, tracking=True)
    display_name = fields.Char(compute='_compute_display_name', store=False, readonly=True)
    date = fields.Date(string='Date', readonly=True, copy=False, tracking=True)
    date_due = fields.Date(string="Due date", readonly=True, copy=False, compute="_compute_date_due")
    ref = fields.Char(string='Reference', copy=False, tracking=True, readonly=True,)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled'), ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    quote_type = fields.Selection(selection=[('quote', 'Quote'), ('estimate', 'Estimate')], string='Type', required=True, store=True, readonly=True, tracking=True, default='quote')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=_get_company_id)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
    tax_ids = fields.Many2many(comodel_name='account.tax', string="Taxes", compute="_compute_tax_ids", readonly=True)
    
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, check_company=True, string='Partner', change_default=True, ondelete='restrict')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="[('company_id', '=', company_id)]", ondelete="restrict", readonly=True,)
    payment_term_id = fields.Many2one('account.payment.term', string='Validity', check_company=True, readonly=True , )

    introduction = fields.Html(string="Introduction", sanitize=True, readonly=True,)
    conditions = fields.Html(string="Conditions", sanitize=True, readonly=True,)

    block_ids = fields.One2many(comodel_name="quote.block", inverse_name="quote_id", string="Blocks", copy=True, readonly=True,)

    # === Amount fields ===
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    # tax_totals = fields.Char(string="Tax Totals", store=True, readonly=True, compute='_compute_totals')
    # binary_tax_totals = fields.Binary(string="Binary Tax Totals", compute='_compute_tax_totals', store=False, readonly=True)
    tax_totals = fields.Binary(compute='_compute_tax_totals', exportable=False)


    @api.depends('block_ids', 'block_ids.amount_untaxed', 'tax_ids')
    def _compute_amount_untaxed(self):
        for record in self:            
            amount_untaxed = 0.0
            for block in record.block_ids:
                amount_untaxed += block.amount_untaxed
            record.amount_untaxed = amount_untaxed


    def _compute_tax_totals(self):
        # 2025/04/07 goede versie !
        AccountTax = self.env['account.tax']
        for quote in self:
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in quote.block_ids]
            AccountTax._add_tax_details_in_base_lines(base_lines, quote.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, quote.company_id)
            quote.binary_tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=quote.currency_id or quote.company_id.currency_id,
                company=quote.company_id,
            )


    def action_post(self):       
        for move in self:
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.block_ids:
                raise UserError(_('You need to add a block before posting.'))
            if not move.partner_id:
                raise UserError(_("The field 'Customer' is required, please complete it to validate the Quote."))
            if float_compare(move.amount_total, 0.0, precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_("You cannot validate a quote with a negative total amount."))
            if not move.date:
                move.date = fields.Date.context_today(self)

        self.write({
            'state': 'posted',
        })

    def _get_report_base_filename(self):
        if self.state == 'draft':
            return _("Draft Quote")

        return self.name

    @api.model
    def _create_quote_number_sequence(self):
        IrSequence = self.env['ir.sequence']
        if IrSequence.search([('code', '=', QUOTE_NUMBER_SEQUENCE_CODE)]):
            return
        
        return IrSequence.sudo().create({
            'name': _("Quote Number Sequence"),
            'padding': 4,
            'code': QUOTE_NUMBER_SEQUENCE_CODE,
            'number_next': 1,
            'number_increment': 1,
            'use_date_range': True,
            'prefix': 'SQ/%(year)s',
            'company_id': False,
        })

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only Draft Quote can be deleted'))

        return super(Quote, self).unlink()
