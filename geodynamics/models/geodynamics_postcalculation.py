
from odoo import api, fields, models, _, tools

class GeodynamicsPostCalculation(models.Model):
    _name = 'geodynamics.postcalculation'
    _description = 'Geodynamics Postcalculation'
    _rec_name = 'date'

    date = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(selection=[('draft','Draft'),('validated','Validated')])
