# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Task(models.Model):
    _inherit = 'project.task'
    _description = "Task extension for progress report"

    include_in_progress_report = fields.Boolean(
        "Include in progress report", related='stage_id.include_in_progress_report', help="Task must be included in progress reports.", readonly=True)

    progress_quantity = fields.Float(
        'Quantity', digits='1.3f', tracking=True, default=0.0)
    progress_unit = fields.Char('Unit', tracking=True, default='sog')
    progress_currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_progress_currency_id', tracking=True)
    progress_unit_price = fields.Monetary('Unit price', digits='Product Price', tracking=True, currency_field='progress_currency_id')

    @api.depends('company_id')
    def _compute_progress_currency_id(self):
        main_company = self.env['res.company']._get_main_company()
        for task in self:
            task.progress_currency_id = task.company_id.sudo().currency_id.id or main_company.currency_id.id

    @api.depends('progress_quantity', 'progress_unit_price')
    def _compute_progress_total_price(self):
        for task in self:
            task.progress_total_price = task.progress_quantity * task.progress_unit_price

    progress_total_price = fields.Monetary('Total price', compute=_compute_progress_total_price, currency_field='progress_currency_id')
    
    progress_percentage = fields.Float("Progress precentage", group_operator="avg", help="Display progress of current task.", tracking=True)

    @api.constrains('progress_percentage')
    def _constrains_progress_percentage(self):
        for task in self:
            if (task.progress_percentage < 0.0 or task.progress_percentage > 1.0):
                raise ValidationError("Progress percentage must be at least 0% and at most 100%")
