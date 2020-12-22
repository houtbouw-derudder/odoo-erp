# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CostFormula(models.Model):

    _name = "cost.formula"
    _description = "Cost formula"
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
