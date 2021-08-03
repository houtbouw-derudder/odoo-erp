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
        'hr'
    ],
    'data': [
        'views/planning_capability_views.xml',
        'views/planning_capability_menuitems.xml'
    ],
    'installable': True,
    'auto_install': True,
}
