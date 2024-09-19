# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Invoicing Sequence',
    'version' : '1.1',
    'author' : 'Ahmad Mustafidul Ibad',
    'summary': 'Invoicing',
    'description': """
        Invoicing
    """,
    'category': 'Accounting/Accounting',
    'depends' : ['base', 'base_setup', 'account'],
    'data': [
        'data/ir_sequence.xml',
        'views/res_users_view.xml'
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
