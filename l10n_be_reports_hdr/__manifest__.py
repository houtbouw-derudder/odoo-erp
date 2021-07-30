# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Belgium - Accounting Reports - Customization',
    'version': '1.1',
    'category': 'Accounting/Localizations/Reporting',
    'description': """
        Customization to accounting reports
    """,
    'depends': [
        'l10n_be_reports', 'account_reports'
    ],
    'data': [
        'data/account_financial_html_report_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}
