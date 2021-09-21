
from odoo import fields, models, api

class ProjectTask(models.Model):
    _inherit = 'project.task'

    time_registration_code = fields.Char('Tijdsregistratie code', required=False, index=True, tracking=True)

    def assign_time_registration_code(self):
        for record in self:
            if record.time_registration_code is None:
                # assign TRC