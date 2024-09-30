# -*- coding: utf-8 -*-
{
    'name': "ati_purchase_ib",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as"""
                  """ subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "ATI - Ibad", # author
    'website': "https://akselerasiteknologi.id", # website
    'category': 'Inventory/Purchase', # category
    'version': '16.0.2.8', # version
    'depends': [
        'base',
        'web',
        'purchase',
        'purchase_request',
        'ati_account_ib',
    ], # dependencies
    "assets": {
        "web.assets_common": [
            "ati_purchase_ib/static/src/scss/view.scss",
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/ati_purchase_data.xml',
        'views/ati_purchase_view.xml',
        'views/purchase_request_view.xml',
        'wizard/gr_report_view.xml',
    ], # data files
    'installable': True, # installable
    'application': True, # application
    'license': 'LGPL-3', # license
}