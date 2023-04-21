
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
    def name_get(self):
        result = []
        for move in self:
            name = move._get_quote_display_name(show_ref=True)
            result.append((move.id, name))
        return result        

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
                
                record.date_due = terms[0].get('date')
            else:
                record.date_due = record.date

    @api.depends('block_ids', 'block_ids.amount_untaxed', 'tax_ids')
    def _compute_totals(self):
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
                logging.getLogger().warning(tax_calc)
                tax_totals = self._get_tax_totals(tax_calc, record.partner_id, record.currency_id)                    
                record.amount_untaxed = tax_calc["total_void"]
                record.tax_totals = dumps(tax_totals)
                record.amount_total = tax_calc["total_included"]

    @api.depends('tax_totals')
    def _compute_binary_tax_totals(self):
        for record in self:
            if record.tax_totals:
                record.binary_tax_totals = loads(record.tax_totals)
            else:
                record.binary_tax_totals = None
            logging.getLogger().warning(record.binary_tax_totals)

    name = fields.Char(string='Number', copy=False, compute='_compute_name', readonly=False, store=True, tracking=True)
    date = fields.Date(string='Date', readonly=True, states={'draft': [('readonly', False)]}, copy=False, tracking=True)
    date_due = fields.Date(string="Due date", readonly=True, states={'draft': [('readonly', False)]}, copy=False, compute="_compute_date_due")
    ref = fields.Char(string='Reference', copy=False, tracking=True, readonly=True, states={'draft': [('readonly', False)]},)
    state = fields.Selection(selection=[('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled'), ], string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    quote_type = fields.Selection(selection=[('quote', 'Quote'), ('estimate', 'Estimate')], string='Type', required=True, store=True, readonly=True, tracking=True, default='quote')
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=_get_company_id)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
    tax_ids = fields.Many2many(comodel_name='account.tax', string="Taxes", compute="_compute_tax_ids", readonly=True)
    
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, states={'draft': [('readonly', False)]}, check_company=True, string='Partner', change_default=True, ondelete='restrict')
    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', domain="[('company_id', '=', company_id)]", ondelete="restrict", readonly=True, states={'draft': [('readonly', False)]},)
    payment_term_id = fields.Many2one('account.payment.term', string='Validity', check_company=True, readonly=True , states={'draft': [('readonly', False)]})

    introduction = fields.Html(string="Introduction", sanitize=True, readonly=True, states={'draft': [('readonly', False)]},)
    conditions = fields.Html(string="Conditions", sanitize=True, readonly=True, states={'draft': [('readonly', False)]},)

    block_ids = fields.One2many(comodel_name="quote.block", inverse_name="quote_id", string="Blocks", copy=True, readonly=True, states={'draft': [('readonly', False)]},)

    # === Amount fields ===
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_compute_totals')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True)
    tax_totals = fields.Char(string="Tax Totals", store=True, readonly=True)
    binary_tax_totals = fields.Binary(string="Tax Totals", compute='_compute_binary_tax_totals', store=False, readonly=True)

    def _get_tax_totals(self, calculation, partner, currency):
        """ Compute the tax totals details for the business documents.

        :return: A dictionary in the following form:
            {
                'amount_total':                 The total amount to be displayed on the document, including every total
                                                types.
                'amount_untaxed':               The untaxed amount to be displayed on the document.
                'formatted_amount_total':       Same as amount_total, but as a string formatted accordingly with
                                                partner's locale.
                'formatted_amount_untaxed':     Same as amount_untaxed, but as a string formatted accordingly with
                                                partner's locale.
                'groups_by_subtotals':          A dictionary formed liked {'subtotal': groups_data}
                                                Where total_type is a subtotal name defined on a tax group, or the
                                                default one: 'Untaxed Amount'.
                                                And groups_data is a list of dict in the following form:
                    {
                        'tax_group_name':                   The name of the tax groups this total is made for.
                        'tax_group_amount':                 The total tax amount in this tax group.
                        'tax_group_base_amount':            The base amount for this tax group.
                        'formatted_tax_group_amount':       Same as tax_group_amount, but as a string formatted accordingly
                                                            with partner's locale.
                        'formatted_tax_group_base_amount':  Same as tax_group_base_amount, but as a string formatted
                                                            accordingly with partner's locale.
                        'tax_group_id':                     The id of the tax group corresponding to this dict.
                    }
                'subtotals':                    A list of dictionaries in the following form, one for each subtotal in
                                                'groups_by_subtotals' keys.
                    {
                        'name':                             The name of the subtotal
                        'amount':                           The total amount for this subtotal, summing all the tax groups
                                                            belonging to preceding subtotals and the base amount
                        'formatted_amount':                 Same as amount, but as a string formatted accordingly with
                                                            partner's locale.
                    }
                'subtotals_order':              A list of keys of `groups_by_subtotals` defining the order in which it needs
                                                to be displayed
            }
        """
        account_tax = self.env['account.tax']

        subtotal_priorities = {}
        grouped_taxes = defaultdict(lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))

        for tax in calculation["taxes"]:
            tax_group = account_tax.browse(tax["id"]).tax_group_id
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                subtotal_title = _('Untaxed Amount')
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            tax_group_vals = grouped_taxes[subtotal_title][tax_group]
            tax_group_vals["base_amount"] += tax["base"]
            tax_group_vals["tax_amount"] += tax["amount"]
            # tax_group_vals["base_line_keys"].add(tax)

        # Compute groups_by_subtotal
        groups_by_subtotal = defaultdict(list)
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' %(subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = [] # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = calculation["total_excluded"] + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(self.env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            'amount_total': calculation["total_included"],
            'amount_untaxed': calculation["total_excluded"],
            'formatted_amount_total': formatLang(self.env, calculation["total_included"], currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, calculation["total_excluded"], currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'subtotals_order': sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]),
            'allow_tax_edition': False,
        }

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
