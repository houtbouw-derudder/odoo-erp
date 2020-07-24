# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ProgressReport(models.Model):
	_name = 'project.progress.report'
	_description = 'A Progress Report for tasks in a project'
