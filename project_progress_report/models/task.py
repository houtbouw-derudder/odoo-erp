# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Task(models.Model):
	_inherit = 'project.task'
	_description = "Task extension for progress report"

	sale_quantity = fields.Float('Quantity', digits='1.3f', tracking=True, default=0.0)
	sale_unit = fields.Char('Unit', tracking=True, default='sog')
	sale_currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_sale_currency_id', tracking=True)
	sale_unit_price = fields.Float('Unit price', digits='Product Price', tracking=True)

	@api.depends('company_id')
	def _compute_sale_currency_id(self):
		main_company = self.env['res.company']._get_main_company()
		for task in self:
			task.sale_currency_id = task.company_id.sudo().currency_id.id or main_company.currency_id.id

	@api.depends('sale_quantity', 'sale_unit_price')
	def _compute_total_sale_price(self):
		for task in self:
			task.total_sale_price = (task.sale_quantity or 1.0) * (task.sale_unit_price or 0.0)

	total_sale_price = fields.Float('Total price', compute=_compute_total_sale_price)

	@api.depends("stage_id")
	def _compute_include_in_progress_report(self):
		return (self[0].stage_id.include_in_progress_report or False) if len(self) == 1 else False

	include_in_progress_report = fields.Boolean('Include in progress report', compute=_compute_include_in_progress_report)
