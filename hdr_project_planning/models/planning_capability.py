
from odoo import fields, models, api

class Capability(models.Model):
    _name = 'hdr.planning.capability'

    name = fields.Char(string='Name',required=True,index=True,tracking=True)
    description = fields.Char(string='Description')
