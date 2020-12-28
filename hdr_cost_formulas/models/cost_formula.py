# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from . import parser


class CostFormula(models.Model):

    _name = "cost.formula"
    _description = "Cost formula"
    _inherit = ['mail.thread']
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True,
                       readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=1)
    active = fields.Boolean(
        default=True, help="If the active field is set to False, it will allow you to hide the project without removing it.")
    state = fields.Selection(selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancelled')],
                             string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')

    parameters = fields.Char(
        string="Parameters", help="Comma separated list of parameter names", tracking=True, readonly=True, states={'draft': [('readonly', False)]})
    view = fields.Text(string='HTML + JavaScript', tracking=True,
                       readonly=True, states={'draft': [('readonly', False)]})

    cost_item_ids = fields.One2many('cost.formula.item', 'cost_formula_id', string='Cost items',
                                    copy=True, readonly=True, states={'draft': [('readonly', False)]})

    @api.constrains('parameters')
    def validate_parameters(self):
        for record in self:
            try:
                parser.validate_parameter_list(record.parameters)
            except parser.ExpressionException as e:
                raise ValidationError("Invalid parameter list: {0}".format(e))

    def action_confirm(self):
        for formula in self:
            if not formula.cost_item_ids:
                raise ValidationError(
                    _("Your formula does not have any cost items"))

            to_write = {'state': 'confirmed'}
            formula.write(to_write)

    def action_cancel(self):
        for formula in self:
            to_write = {'state': 'cancel'}
            formula.write(to_write)

    def action_draft(self):
        for formula in self:
            to_write = {'state': 'draft'}
            formula.write(to_write)


class CostItem(models.Model):
    _name = "cost.formula.item"
    _description = "Cost item"
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)

    cost_formula_id = fields.Many2one('cost.formula', string='Cost formula', index=True, required=True,
                                      readonly=True, auto_join=True, ondelete="cascade", help="The cost formula of this item.")

    condition = fields.Char(string="Condition", required=False)
    quantity_expression = fields.Char(
        string="Quantity expression", required=True)
    product_id = fields.Many2one('product.product', string='Product')

    @api.constrains('condition', 'cost_formula_id')
    def validate_condition(self):
        for record in self:
            if record.condition:
                try:
                    parser.validate_logical_expression(
                        record.condition, record.cost_formula_id.parameters)
                except parser.ExpressionException as e:
                    raise ValidationError("Invalid condition: {0}".format(e))

    @api.constrains('quantity_expression', 'cost_formula_id')
    def validate_quantity_expression(self):
        for record in self:
            try:
                parser.validate_math_expression(
                    record.quantity_expression, record.cost_formula_id.parameters)
            except parser.ParseException as e:
                raise ValidationError(
                    "Invalid quantity expression: {0}".format(e))
