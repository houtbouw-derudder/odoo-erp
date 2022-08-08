
from odoo import api, fields, models


class PurchaseItem(models.Model):
    _name = 'hdr.purchase.item'
    _description = "Aan te kopen item voor een bepaald project"
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    state = fields.Selection(selection=[('to_order', 'To order'), ('ordered', 'Ordered'),('deliverd', 'Delivered')], default='to_order')
    project_id = fields.Many2one('project.project', 'Project')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    description = fields.Html()
    quantity = fields.Char()
    budget = fields.Char()

    def action_mark_as_to_order(self):
        pass

    def action_mark_as_ordered(self):
        pass

    def action_mark_as_delivered(self):
        pass
    