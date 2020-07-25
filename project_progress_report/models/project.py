# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Project(models.Model):
    _inherit = 'project.project'
    _description = "Project extension for progress report"

    progress_reports = fields.One2many(
        'project.progress.report', 'project_id', string="Progress Reports")

    def _compute_progress_reports_count(self):
        for project in self:
            project.progress_reports_count = len(project.progress_reports) or 0

    progress_reports_count = fields.Integer(
        string='Progress report count', compute='_compute_progress_reports_count')
