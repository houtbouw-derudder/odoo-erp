
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_basic_auth_header = fields.Char(config_parameter='geodynamics.api_basic_auth_header', string="Basic Auth header")
    