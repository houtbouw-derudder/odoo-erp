
from odoo import fields, models, api

class Capability(models.Model):
    name = fields.Char(string='Name',required=True,index=True,tracking=True)
    description = fields.Char(string='Description')
