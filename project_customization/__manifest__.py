# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project - Customization',
    'version': '1.0',
    'category': 'Customization',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Customization to project app
    """,
    'depends': [
        'project'
    ],
    'data': [
        'views/project_views.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': False,
    'license': 'OPL-1'
}
