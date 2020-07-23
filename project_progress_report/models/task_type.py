# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskType(models.Model):
	_inherit = 'project.task.type'
	_description = "Task-type extension for progress report"

	include_in_progress_report = fields.Boolean(string='Include in progress report')
