# -*- coding: utf-8 -*-
{
    'name': "AGP Keuangan",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as"""
                  """ subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Abhimantra - Ibad", # author
    'website': "https://abhimantra.co.id/", # website
    'category': 'Accounting/Keuangan', # category
    'version': '16.0.0.4', # version
    'depends': [
        'base',
        'base_setup',
        'mail',
        'account',
    ], # dependencies
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'views/menuitem.xml',
    ], # data files
    'installable': True, # installable
    'application': True, # application
    'license': 'LGPL-3', # license
}