
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    geo_company_name = fields.Char(config_parameter='geodynamics.company_name', string="Company name")
    user_name = fields.Char(config_parameter='geodynamics.user_name',string='User name')
    password = fields.Char(config_parameter='geodynamics.password',string='Password')