# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Geodynamics',
    'version': '1.0',
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
        'views/geodynamics_postcalculation_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1'
}
