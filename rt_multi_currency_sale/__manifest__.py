# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales - Multi Currency',
    'version': '1.0.0',
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    'depends': ['sale_management','rt_multi_currency_account'],
    'summary': 'Allows you to display a second currency in the sales module',
    'description': '''
        Add "Monetary" fields to sales to display various fields in the
        secondary currency, edit the summary in the reports to visualize
        the total in the second currency.
    ''',
    'license' : "LGPL-3",
    'application' : True,
    'installable' : True,
    'data' : [
        'reports/ir_actions_report_templates.xml',
        'views/sale_order_views.xml',
    ]
}
