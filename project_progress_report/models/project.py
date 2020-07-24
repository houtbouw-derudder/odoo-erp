# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project extension for progress report"
	