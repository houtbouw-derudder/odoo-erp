# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskProgress(models.Model):
    _name = 'project.task.progress'
    _description = 'The progress of a task at the time the progress report was generated'

    progress_report_id = fields.Many2one('project.progress.report', string='Progress report')
    task_id = fields.Many2one('project.task', string="Project")
    progress_quantity = fields.Float('Quantity')
    progress_unit = fields.Char('Unit')
    progress_currency_id = fields.Many2one('res.currency', 'Currency')
    progress_unit_price = fields.Float('Unit price')
    progress_total_price = fields.Float('Total price')
    progress_percentage = fields.Float("Progress precentage")
    