# -*- coding: utf-8 -*-
{
    "name": "fiscal_printer_pos",
    "summary": """Fiscal Printer for POS""",
    "description": """""",
    'author': '',
    'company': '',
    'maintainer': '',
    'website': '',
    'category': 'Localization',
    "version": "0.1",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "depends": ["base", "point_of_sale", "fiscal_printer"],
    "data": [
        # 'security/ir.model.access.csv',
        "views/pos_payment_method.xml",
        "views/pos_order.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "fiscal_printer_pos/static/src/js/models.js",
            # "fiscal_printer_pos/static/src/js/pos.js",
            "fiscal_printer_pos/static/src/js/Screens/PartnerListScreen/PartnerDetailsEdit.js",
            "fiscal_printer_pos/static/src/js/Screens/PaymentScreen/PaymentScreen.js",
            "fiscal_printer_pos/static/src/js/Screens/ReceiptScreen/ReceiptScreen.js",
            "fiscal_printer_pos/static/src/xml/Screens/ReceiptScreen/ReceiptScreen.xml",
            "fiscal_printer_pos/static/src/xml/Screens/ClientListScreen/ClientDetailsEdit.xml",
        ]
    },
}
