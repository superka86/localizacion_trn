# -*- coding: utf-8 -*-
{
    'name': "Portal BDV Payments",

    'summary': """
        Payments from portal clients to Venezuela Bank BDV""",

    'description': """
        Payments from portal clients to Venezuela Bank BDV 
    """,
    'author': "INGEINT C.A",
    'website': "http://www.ingeint.com",
    'category': 'Services',
    'version': '17.0.0.1',
    'depends': ['base', 'account', 'contacts', 'portal' , 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/bdv_config_views.xml',
        'views/bdv_transaction.xml',
        'views/portal_templates.xml',
        'views/portal_p2p_templates.xml',
        'data/payment_acquirer_data.xml',
        'data/payment_transaction_sequence.xml',
        'data/bdv_ipg_cron.xml',
        'data/ir_config_parameters.xml',
        'data/account_payment_method.xml'
    ],
    'license': 'LGPL-3',
}
