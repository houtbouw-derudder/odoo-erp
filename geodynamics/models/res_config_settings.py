
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    api_basic_auth_header = fields.Char(config_parameter='geodynamics.api_basic_auth_header', string="Basic Auth header")
    company_name = fields.Char(config_parameter='geodynamics.company_name', string="Company name")
    user_name = fields.Char(config_parameter='geodynamics.user_name',string='User name')
    password = fields.Char(config_parameter='geodynamics.password',string='Password')