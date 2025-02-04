# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Account - Multi Currency",
    "version": "1.0.5",
    "depends": ["account"],
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "summary": "Allows you to display a second currency in the Account module",
    "description": """
        Add 'monetary' type fields to show a second currency,
        Add the option of a second currency to visualize invoices in the
        Configuration menu, creates a component

            'second-account-tax-totals-field'

        To visualize the summary in the second currency in the invoices and annexes
        This summary to system reports
    """,
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "data": [
        "reports/report_invoice.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "views/product_template_view.xml",
    ],
    "assets": {
        "web.assets_backend": ["rt_multi_currency_account/static/src/components/**/*"]
    },
}
