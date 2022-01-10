# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Geodynamics',
    'version': '2.0',
    'category': 'Customization',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Integration with geodynamics
    """,
    'depends': [
        'project',
        'hr_timesheet'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/geodynamics_views.xml',
        'views/res_config_settings_views.xml',
        'views/geodynamics_reporting_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1'
}
