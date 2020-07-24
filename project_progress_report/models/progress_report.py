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
                                 index=True, tracking=True, required=True)
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

    def _do_update_task_progress(self):
        self.ensure_one()

    def update_task_progress(self):
        for report in self:
            report._do_update_task_progress()

    def _do_post(self):
        self.ensure_one()

        to_write = {'state': 'approved', 'name': self.name}
        if not self.name:
            to_write['name'] = self.env['ir.sequence'].next_by_code(
                'project.progress.report', sequence_date=self.date)
        self.write(to_write)

    def post(self):
        for report in self:
            report._do_post()
