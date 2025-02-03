# -*- coding: utf-8 -*-
{
    'name': "Purchase Report",
    'summary': "Purchase Report",
    'description': "Generate purchase book by fiscal date",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    'version': '1.0.0',
    'depends': ['account','purchase','retenciones','report_xlsx'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',

        'data/purchase_report_paperformat.xml',
        'reports/purchase_report_template_views.xml',

        'views/purchase_report_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
}
