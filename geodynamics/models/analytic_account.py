
from odoo import fields, models

class AnalyticAccountLine(models.Model):
    _inherit = 'analytic.account.line'

    postcalculation_line_id = fields.Many2one('geodynamics.postcalculation.line', 'Postcalculation Line', required=False, ondelete='cascade', index=True)
