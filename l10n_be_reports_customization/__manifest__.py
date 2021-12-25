# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HDR - Belgium - Accounting Reports - Customization',
    'version': '1.1',
    'category': 'Accounting/Localizations/Reporting',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Accounting reports for Belgium - Customization
        - change Profit & Loss report: split 60 and 61
        - add NBK & BBK to Executive Report
    """,
    'depends': [
        'l10n_be_reports',
        'account_reports'
    ],
    'data': [
        'data/account_financial_html_report_data.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1'
}
