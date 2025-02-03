# -*- coding: utf-8 -*-
{
    'name': "Sales Book",
    'summary': "sales book report",
    'description': "Generate sales book report by fiscal date",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    'version': '1.0.0',
    'depends': ['account','tribute_fields','report_xlsx'],
    'license': 'LGPL-3',
    "application": True,
    "installable": True,
    'data': [
        'security/ir.model.access.csv',
        'reports/sales_book_report_views.xml',
        'views/sales_book_views.xml',
        'views/menu_views.xml',
    ],
}