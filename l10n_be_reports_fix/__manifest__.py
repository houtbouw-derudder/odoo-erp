# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgium - Accounting Reports - Fix',
    'version': '1.1',
    'category': 'Accounting/Localizations/Reporting',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Accounting reports for Belgium - Fix
        - change Profit & Loss report: split 60 and 61
    """,
    'depends': [
        'l10n_be_reports'
    ],
    'data': [
        'data/account_financial_html_report_data.xml'
    ],
    'installable': True,
    'auto_install': True
}
