# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HDR Sales',
    'version': '0.1',
    'category': 'Sales',
    'author': 'Houtbouw De Rudder bv',
    'description': """
        Sales
    """,
    'depends': [
        'base', 'mail'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sales_views.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1'
}
