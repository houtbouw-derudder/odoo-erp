# -*- coding: utf-8 -*-

from odoo import models, fields, api

class TaskProgress(models.Model):
    _name = 'project.task.progress'
    _description = 'The progress of a task at the time the progress report was generated'

    progress_report_id = fields.Many2one('project.progress.report', string='Progress report', readonly=True)
    task_id = fields.Many2one('project.task', string="Project", readonly=True)
    progress_quantity = fields.Float('Quantity', readonly=True)
    progress_unit = fields.Char('Unit', readonly=True)
    progress_currency_id = fields.Many2one('res.currency', 'Currency', readonly=True)
    progress_unit_price = fields.Float('Unit price', readonly=True)
    progress_total_price = fields.Float('Total price', readonly=True)
    progress_percentage = fields.Float("Progress precentage", readonly=True)
    