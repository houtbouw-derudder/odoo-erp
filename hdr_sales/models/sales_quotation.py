
from odoo import api, fields, models, _


class Quotation(models.Model):
    _name = 'hdr_sales.quotation'
    _description = 'Sales quotation'
    _inherit = ['mail.thread'] 

    name = fields.Char(string='Number', copy=False, readonly=False, store=True, index=True, tracking=True)
    date = fields.Date(
        string='Date',
        required=True,
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        copy=False,
        tracking=True,
        default=fields.Date.context_today
    )
    ref = fields.Char(string='Reference', copy=False, tracking=True)

    state = fields.Selection(selection=[('draft', 'Draft'),('posted', 'Posted'),('cancel', 'Cancelled'),], string="Status", required=True, readonly=True, copy=False, tracking=True, default="draft")
    document_type = fields.Selection(selection=[('quotation', 'Quotation'),('estimate', 'Estimate'),], string="Type", required=True, store=True, index=True, readonly=True, tracking=True, default="quotation")
    company_id = fields.Many2one(comodel_name='res.company', string='Company', store=True, readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one(string='Company Currency', readonly=True, related='company_id.currency_id')
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True, states={'draft': [('readonly', False)]}, check_company=True, string='Partner', change_default=True)

    line_ids = fields.One2many('hdr_sales.quotation.lines', 'quotation_id', string="Quotation Lines")

    intro = fields.Html(sanitize=True)
    outro = fields.Html(sanitize=True)

    total_amount_untaxed = fields.Monetary(store=True)

class QuotationLine(models.Model):
    _name = 'hdr_sales.quotation.lines'
    _description = 'Sales quotation line'

    quotation_id = fields.Many2one("hdr_sales.quotation", string="Quotation", store=True, ondelete="cascade", required=True, index=True)

    currency_id = fields.Many2one(related='quotation_id.company_currency_id', depends=["quotation_id"], store=True, ondelete="restrict", readonly=True)

    name = fields.Char(copy=False, readonly=False)
    description = fields.Html(sanitize=True)
    price = fields.Monetary(store=True)