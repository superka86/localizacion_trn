# -*- coding: utf-8 -*-
{
    "name": "Inventory resume",
    "summary": "summary",
    "description": "Description",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "version": "1.0.0",
    "depends": ["account", "stock", "report_xlsx"],
    "license": "LGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/rt_inventory_resume.xml",
        "views/rt_inventory_resume_line.xml",
        "wizard/monthly_resume_wizard_view.xml",
        "report/rt_inventory_report.xml",
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_common": [
            "rt_inventory_book/static/src/js/monthly_inventory_resume_controller.js"
        ],
        "web.assets_backend": [
            "rt_inventory_book/static/src/xml/monthly_inventory_resume.xml"
        ],
    },
}
