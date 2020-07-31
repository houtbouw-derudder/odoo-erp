# -*- coding: utf-8 -*-


from odoo.http import request
from odoo import models, api

class ReportProgressReport(models.AbstractModel):
    _name = 'report.project_progress_report.report_progress_report'
    _description = "Project progress report"

    def _get_report_values(self, docids, data=None):        
        report_obj = self.env['ir.actions.report']
        report = report_obj._get_report_from_name('project_progress_report.report_progress_report')

        progress_reports = self.env['project.progress.report'].browse(docids)

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': progress_reports,
        }
        return docargs
