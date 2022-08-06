
from odoo import api, fields, models


class PurchaseItem(models.Model):
    _name = 'hdr.purchase.item'
    _description = "Aan te kopen item voor een bepaald project"
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    project_id = fields.Many2one('project.project', 'Project')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    description = fields.Html()
    quantity = fields.Char()
    budget = fields.Char()
    