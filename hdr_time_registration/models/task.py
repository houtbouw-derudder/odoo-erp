
from odoo import fields, models, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    time_registration_code = fields.Char(
        'Tijdsregistratie code', required=False, index=True, tracking=True)

    def assign_time_registration_code(self):
        for record in self:
            if not record.time_registration_code:
                record.time_registration_code = "%s" % self.env['ir.sequence'].next_by_code(
                    'task.time_registration_code')
                ir_model_data = self.sudo().env['ir.model.data']
                ir_model_data.create({
                    'model': self._name,
                    'res_id': self.id,
                    'module': 'trc',
                    'name': record.time_registration_code,
                })
