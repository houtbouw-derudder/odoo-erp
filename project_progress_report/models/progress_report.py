# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProgressReport(models.Model):
	_name = 'project.progress.report'
	_description = 'A Progress Report for tasks in a project'

	project_id = fields.Many2one('project.project', string='Project', default=lambda self: self.env.context.get('default_project_id'),
        index=True, tracking=True, check_company=True)
