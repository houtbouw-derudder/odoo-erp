# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HDR Invoice document',
    'version': '2.0',
    'category': 'Accounting/Localizations',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Custom Invoice Document
    """,
    'depends': [
        'account'
    ],
    'data': [
        'views/report_invoice.xml',
        'views/account_report.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1'
}
