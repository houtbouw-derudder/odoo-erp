# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CostFormula(models.Model):

    _name = "cost.formula"
    _description = "Cost formula"
    _inherit = ['mail.thread']
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(
        default=True, help="If the active field is set to False, it will allow you to hide the project without removing it.")
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancelled')],
                             string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    parameters = fields.Char(
        string="Parameters", help="Comma separated list of parameter names", tracking=True)
    view = fields.Text(string='HTML + JavaScript', tracking=True)

    def action_post(self):
        raise UserError(_("Not implemented"))

    def action_cancel(self):
        raise UserError(_("Not implemented"))

    def action_draft(self):
        raise UserError(_("Not implemented"))


class CostItem(models.Model):
    _name = "cost.item"
    _description = "Cost item"
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
    condition = fields.Char(string="Condition", required=False)
    quantity_expression = fields.Char(
        string="Quantity expression", required=True)
