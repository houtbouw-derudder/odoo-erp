
from odoo import fields, models, api

class Capability(models.Model):
    _name = 'hdr.planning.capability'
    _description = 'A capability to assing to a resource in order to make a resource capacity planning'

    name = fields.Char(string='Name',required=True,index=True)
    description = fields.Char(string='Description')

class Resource(models.Model):
    _name = 'hdr.planning.resource'
    _description = 'Information on a resource: capability, availability'

    employee_id = fields.Many2one('hr.employee', string='Werknemer', required=True)
    # capability_ids = None
    # available_hours_per_week = None