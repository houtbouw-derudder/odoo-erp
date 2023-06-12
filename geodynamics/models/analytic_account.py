
from odoo import fields, models

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    postcalculation_line_id = fields.Many2one('geodynamics.postcalculation.line', 'Postcalculation Line', required=False, ondelete='cascade', index=True)
