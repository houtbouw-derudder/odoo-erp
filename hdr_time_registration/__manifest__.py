# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HDR - Time Registration',
    'version': '1.0',
    'category': 'Customization',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Customization for time registration with Intellitracer
    """,
    'depends': [
        'project',
        'hr_timesheet'
    ],
    'data': [
        'data/ir.sequence.xml',
        'views/project_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'OPL-1'
}
