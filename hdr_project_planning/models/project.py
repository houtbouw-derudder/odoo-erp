
from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    capability_id = fields.Many2one('hdr.planning.capability', string='Competentie', required=False)
