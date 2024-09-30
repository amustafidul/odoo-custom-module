# -*- coding: utf-8 -*-
{
    'name': "ati_reminder_sertifikat", # name
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as"""
                  """ subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "ATI - Ibad", # author
    'website': "https://akselerasiteknologi.id", # website
    'category': 'Reminder/Sertifikat', # category
    'version': '16.0.0.2', # version
    'depends': [
        'base',
        'hr',
    ], # dependencies
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_cron.xml',
        'security/ir.model.access.csv',
        'views/reminder_sertifikat_view.xml',
    ], # data files
    'installable': True, # installable
    'application': True, # application
    'license': 'LGPL-3', # license
}