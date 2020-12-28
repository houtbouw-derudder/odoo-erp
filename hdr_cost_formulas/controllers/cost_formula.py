# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.http import Controller, route

class CostFormulaController(Controller):

    @route(route='/cost_formulas/evaluate', type='http', methods=['POST'], csrf=False, auth='public', website=False)
    def evaluate(self):
        return json.dumps({'result': 'ok'})
