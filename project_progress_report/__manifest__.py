# -*- coding: utf-8 -*-
{
    'name': "Project Progress Report",

    'summary': """Manage progress reports""",

    'description': """""",

    'author': "Houtbouw De Rudder bv",
    'website': "https://www.houtbouw-derudder.be",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Project',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['project'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'templates.xml',
        'data/progress_report_data.xml',
        'views/task_views.xml',
        'views/task_type_views.xml',
        'views/progress_report_views.xml',
        'views/project_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}