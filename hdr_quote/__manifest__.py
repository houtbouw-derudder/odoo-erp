# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Quote',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Sales
    """,
    'depends': [
        'base', 'mail', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/quote_views.xml',
        'views/report_quote.xml',
        'views/quote_report.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1'
}
