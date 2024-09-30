# -*- coding: utf-8 -*-
{
    'name': "ati_hr_ib",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as"""
                  """ subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "ATI - Ibad", # author
    'website': "https://akselerasiteknologi.id", # website
    'category': 'Human Resources/Employees', # category
    'version': '15.0.1.1', # version
    'depends': [
        'base',
        'hr',
    ], # dependencies
    'data': [
        'views/hr_department_view.xml',
    ], # data files
    'installable': True, # installable
    'application': True, # application
    'license': 'LGPL-3', # license
}