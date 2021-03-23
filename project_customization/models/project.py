# -*- coding: utf-8 -*-

from odoo import models

class Project(models.Model):
    _inherit = "project.project"

    def action_view_account_analytic_line_2(self):
        return super(Project, self).action_view_account_analytic_line()

    def action_view_crossover_budget_lines(self):
        """ return the action to see all the budget lines of the project's analytic account """
        action = self.env["ir.actions.actions"]._for_xml_id("account_budget.act_account_analytic_account_cb_lines")
        action['context'] = {'default_analytic_account_id': self.analytic_account_id.id, 'search_default_analytic_account_id': [self.analytic_account_id.id]}
        return action
