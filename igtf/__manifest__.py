{
    "name": "IGTF",
    "version": "1.0.0",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "depends": ["base","account"],
    "summary": "Activates the tax on large financial transactions",
    "description": """
        This module modifies the payment by adding an additional 3%
        on the amount paid in the cases applied the IGTF.
    """,
    "license" : "LGPL-3",
    'application' : True,
    'installable' : True,
    "data": [
        "wizards/account_payment_register_view.xml",
        "views/res_config_settings_view.xml",
        "views/account_journal_view.xml",
        "views/account_move_view.xml",
        "views/account_payment_view.xml",
    ],
}