# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TaskProgress(models.Model):
    _name = 'project.task.progress'
    _description = 'The progress of a task at the time the progress report was generated'

    progress_report_id = fields.Many2one(
        'project.progress.report', string='Progress report', readonly=True, required=True)
    task_id = fields.Many2one('project.task', string="Task", readonly=True, required=True)
    progress_quantity = fields.Float('Quantity', readonly=True)
    progress_unit = fields.Char('Unit', readonly=True)
    progress_currency_id = fields.Many2one(
        'res.currency', 'Currency', readonly=True)
    progress_unit_price = fields.Monetary('Unit price', readonly=True, currency_field='progress_currency_id')
    progress_total_price = fields.Monetary('Total price', readonly=True, currency_field='progress_currency_id')
    progress_percentage = fields.Float("Progress precentage", readonly=True)
    progress_price = fields.Monetary('Progress price', readonly=True, currency_field='progress_currency_id')
