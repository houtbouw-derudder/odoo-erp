# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class ProgressReport(models.Model):
    _name = 'project.progress.report'
    _description = 'A Progress Report for tasks in a project'

    name = fields.Char(string='Number', required=True,
                       readonly=True, copy=False, default='/')
    date = fields.Date(string='Date', required=True, index=True, readonly=True,
                       states={'draft': [('readonly', False)]},
                       default=fields.Date.context_today)
    project_id = fields.Many2one('project.project', string='Project', default=lambda self: self.env.context.get('default_project_id'),
                                 index=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')

    task_progess_ids = fields.One2many('project.task.progress', 'progress_report_id',
                                       string="Task progress", readonly=True, states={'draft': [('readonly', False)]})

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
        
        self.task_progess_ids.unlink()

        stage_ids = []
        for stage in self.project_id.type_ids.filtered(lambda s: s.include_in_progress_report == True):
            stage_ids.append(stage.id)

        if len(stage_ids) == 0:
            return
        
        tasks = self.env['project.task'].search([('project_id', '=', self.project_id.id), ('stage_id', 'in', stage_ids)])
        TaskProgress = self.env['project.task.progress']
        for task in tasks:
            task_progress_values = {}
            task_progress_values['progress_report_id'] = self.id
            task_progress_values['task_id'] = task.id
            task_progress_values['progress_quantity'] = task.progress_quantity
            task_progress_values['progress_unit'] = task.progress_unit
            task_progress_values['progress_currency_id'] = task.progress_currency_id.id
            task_progress_values['progress_unit_price'] = task.progress_unit_price
            task_progress_values['progress_total_price'] = task.progress_total_price
            task_progress_values['progress_percentage'] = task.progress_percentage
            TaskProgress.create([task_progress_values])

    def update_task_progress(self):
        for report in self:
            report._do_update_task_progress()

    def _do_post(self):
        self.ensure_one()

        to_write = {'state': 'approved', 'name': self.name}
        if self.name == '/':
            to_write['name'] = self.env['ir.sequence'].next_by_code(
                'project.progress.report', sequence_date=self.date)
        self.write(to_write)

    def post(self):
        for report in self:
            report._do_post()
