# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProgressReport(models.Model):
    _name = 'project.progress.report'
    _description = 'A Progress Report for tasks in a project'

    name = fields.Char(string='Number', required=True,
                       readonly=True, copy=False, default='/')
    date = fields.Date(string='Date', required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=fields.Date.context_today)
    project_id = fields.Many2one('project.project', string='Project', default=lambda self: self.env.context.get('default_project_id'),
                                 index=True, tracking=True, check_company=True, required=True)
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    @api.depends('name', 'state')
    def name_get(self):
        result = []
        for report in self:
            if report.state == 'draft':
                name = _("Draft")
            else:
                name = report.name
            result.append((report.id, name))
        return result
