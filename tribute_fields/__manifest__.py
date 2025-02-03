# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Tribute Fields",
    "version": "1.0.0",
    "depends": ["base", "contacts", "account"],
    "description": """
        Add the necessary fields for the Registry
        of Fiscal Information in other modules.
    """,
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "license": "LGPL-3",
    "installable": True,
    "data": [
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/account_move_views.xml",
        "views/menu_views.xml",
    ],
}