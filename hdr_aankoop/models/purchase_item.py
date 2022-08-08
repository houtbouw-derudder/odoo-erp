
from odoo import api, fields, models, _


class PurchaseItem(models.Model):
    _name = 'hdr.purchase.item'
    _description = "Aan te kopen item voor een bepaald project"
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    state = fields.Selection(selection=[('to_order', 'To order'), ('ordered', 'Ordered'),('delivered', 'Delivered')], default='to_order')
    project_id = fields.Many2one('project.project', 'Project')
    supplier_id = fields.Many2one('res.partner', 'Supplier')
    description = fields.Html()
    quantity = fields.Char()
    budget = fields.Char()

    def action_mark_as_to_order(self):
        for record in self:
            record.state = 'to_order'
            record.message_post(body=_("<p>State -> To order</p>"))

    def action_mark_as_ordered(self):
        for record in self:
            record.state = 'ordered'
            record.message_post(body=_("<p>State -> Ordered</p>"))

    def action_mark_as_delivered(self):
        for record in self:
            record.state = 'delivered'
            record.message_post(body=_("<p>State -> Delivered</p>"))
    