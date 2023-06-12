# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HDR - Belgium - Accounting Reports - Customization',
    'version': '1.2',
    'category': 'Accounting/Localizations/Reporting',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Accounting reports for Belgium - Customization
        - change Profit & Loss report: split 60 and 61
        - add NBK & BBK to Executive Report
    """,
    'depends': [
        'account',
        'l10n_be',
        'l10n_be_reports',
        'account_reports'
    ],
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1'
}
