# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Retentions",
    "version": "1.1.0",
    'author': 'RicardoTeran.Net',
    'company': 'RicardoTeran.Net, S.A.',
    'maintainer': 'https://github.com/ricadoterannet',
    'website': 'https://www.ricardoteran.net',
    'category': 'Localization',
    "depends": ["base", "tribute_fields"],
    "summary": "Module in charge of the creation and management of withholdings",
    "description": """
        This module creates a new model that is responsible for registering
        several invoices to which retentions are applied, it also generates
        reports related to retention (PDF and TXT) and the corresponding seats.
    """,
    "license": "LGPL-3",
    "application": True,
    "installable": True,
    "data": [
        "data/data_retention_default_journals.xml",
        "data/retention_sequence.xml",
        "report/retention_report_views.xml",
        "report/retention_text_report.xml",
        "report/retention_report.xml",
        "report/account_move_retention_report_views.xml",
        "report/account_move_retention_report_template.xml",
        "views/retention_views.xml",
        "views/retention_line_views.xml",
        "views/retention_tax_views.xml",
        "views/account_move.xml",
        "views/res_partner_view.xml",
        "views/menus_view.xml",
        "views/res_config_settings.xml",
        "wizards/account_move_retention_wizard_views.xml",
        "security/ir.model.access.csv",
    ],
    "demo": ["demo/retention_demo_data.xml"],
}
