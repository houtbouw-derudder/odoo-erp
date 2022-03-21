
from odoo import api, fields, models, _


class Quotation(models.Model):
    _name = 'hdr_sales.quotation'
    _description = 'Sales quotation'

    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('validated', 'Validated')], default='draft')
