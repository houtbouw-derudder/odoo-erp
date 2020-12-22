# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CostFormula(models.Model):

    _name = "cost.formula"
    _description = "Cost formula"
    _order = 'sequence, id'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(default=1)

    parameters = fields.Char(string="Parameters", help="Comma separated list of parameter names")
    view = fields.Text(string='HTML + JavaScript')

class CostItem(models.Model):
    _name = "cost.item"
    _description = "Cost item"
    _order = 'sequence, id'

    sequence = fields.Integer(default=1)
