# -*- coding: utf-8 -*-

from odoo import models

class Project(models.Model):
    _inherit = "project.project"

    def action_view_account_analytic_line_2(self):
        return super(Project, self).action_view_account_analytic_line()
