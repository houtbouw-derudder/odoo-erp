# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import Controller, route

class CostFormulaController(Controller):

    @route(route='/cost_formulas/evaluate', type='json', methods=['POST'], csrf=False, auth='none', website=False)
    def evaluate(self):
        return json.dumps({'result': 'ok'})
