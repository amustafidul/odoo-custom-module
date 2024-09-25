# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Qweb Reporting Ib',
    'version' : '1.1',
    'author' : 'Ahmad Mustafidul Ibad',
    'summary': 'Qweb-reporting',
    'description': """
        Qweb-reporting
    """,
    'category': 'Qweb',
    'depends' : ['base', 'base_setup', 'web', 'account'],
    'data': [
        'report/subscription_con_report_templates.xml',
        'report/subscription_con_reports.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
