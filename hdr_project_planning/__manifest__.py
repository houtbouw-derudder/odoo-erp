# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Project Planning',
    'version': '1.0',
    'category': 'Customization',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Customization for project planning
    """,
    'depends': [
        'hr',
        'project',
        'hr_timesheet'
    ],
    'data': [
        'views/project_views.xml',
        'views/planning_views.xml',
        'views/planning_menuitems.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': True,
}
