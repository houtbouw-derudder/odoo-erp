# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskProgress(models.Model):
	_name = 'project.task.progress'
	_description = 'The progress of a task at the time the progress report was generated'

	progress_report_id = fields.Many2one('project.progress.report', string='Progress report', default=lambda self: self.env.context.get('default_progress_report_id'),
        index=True, tracking=True)
	
	