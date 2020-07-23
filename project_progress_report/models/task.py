
from odoo import models, fields, api

class Task(models.Model):
	_inherit = 'project.task'
	_description = "Task extension for progress report"

	sale_currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_sale_currency_id')
	sale_price = fields.Float('Price', digits='Product Price', tracking=True)

	@api.depends('company_id')
	def _compute_sale_currency_id(self):
		main_company = self.env['res.company']._get_main_company()
		for task in self:
			task.sale_currency_id = task.company_id.sudo().currency_id.id or main_company.currency_id.id
