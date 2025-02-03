# -*- coding: utf-8 -*-
{
    "name": "Point Of Sale - Multi Currency",
    "version": "1.0.0",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "depends": ["point_of_sale", "rt_multi_currency_account"],
    "summary": "Allows to visualize a second reference currency in the POS interface",
    "description": """
        Add a second currency in the items of the products,
        in the order and in the payment methods
    """,
    "category": "localization",
    "license": "LGPL-3",
    "application" : True,
    "installable" : True,
    "data": ["views/pos_payment_method_views.xml"],
    "assets": {
        "point_of_sale.assets": [
            "rt_multi_currency_pos/static/src/js/**/*.js",
            "rt_multi_currency_pos/static/src/xml/**/*.xml"
        ],
    }
}
