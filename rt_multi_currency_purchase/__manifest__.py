# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Purchase - Multi Currency',
    'version': '1.0.0',
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    'depends': ['purchase','rt_multi_currency_account'],
    'summary': 'Allows you to display a second currency in the purchase module',
    'description': '''
        Add "Monetary" fields to purchases to display various fields in the
        secondary currency, edit the summary in the reports to visualize
        the total in the second currency.
    ''',
    'license' : "LGPL-3",
    'application' : True,
    'installable' : True,
    'data' : [
        'reports/purchase_order_templates.xml',
        'views/purchase_order_views.xml',
    ]
}
