# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import models, api

import logging

_logger = logging.getLogger(__name__)


class ReportProgressReport(models.AbstractModel):
    _name = 'report.project_progress_report.report_progress_report'
    _description = "Project progress report"

    def _get_report_values(self, docids, data=None):        
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('project_progress_report.report_progress_report')

        progress_reports = self.env['project.progress.report'].browse(docids)

        data = []
        for progress_report in progress_reports:
            val = {}
            val['name'] = progress_report.name
            val['date'] = progress_report.date
            val['project_id'] = progress_report.project_id
            val['previous_progress_report_id'] = progress_report.previous_progress_report_id
            val['task_progress_ids'] = progress_report.task_progress_ids
            data.append(val)

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': data,
        }
        return docargs