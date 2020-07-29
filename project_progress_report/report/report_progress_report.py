# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import models, api

import logging

_logger = logging.getLogger(__name__)


class ReportProgressReport(models.AbstractModel):
    _name = 'report.project_progress_report.report_progress_report'
    _description = "Project progress report"

    def _get_report_values(self, docids, data=None):
        _logger.warning(docids)
        _logger.warning(data)
        
        report_obj = self.env['ir.actions.report']
        _logger.warning(report_obj)
        report = report_obj._get_report_from_name('project_progress_report.report_progress_report')
        _logger.warning(report)

        docs = self.env['project.progress.report'].browse(docids)

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': docs,
        }
        return docargs