# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskType(models.Model):
	_inherit = 'project.task.type'
	_description = "Task-type extension for progress report"
