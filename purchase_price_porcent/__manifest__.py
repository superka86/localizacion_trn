# -*- coding: utf-8 -*-
{
    'name': "purchase_price_porcent",

    'summary': """Porcentaje de precio por compras""",

    'description': """
        Long description of module's purpose
    """,

    'author': 'RicardoTeran.Net',
    'company': 'RicardoTeran.Net, S.A.',
    'maintainer': 'https://github.com/ricadoterannet',
    'website': 'https://www.ricardoteran.net',
    'category': 'Localization',
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'localization',
    'version': '0.1',
    "license": "LGPL-3",
    'application' : True,
    'installable' : True,
    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_sale_price_view.xml',
        'views/purchase_order_view.xml'
    ],
}
