from odoo import fields, models


FISCAL_TYPE_SEL = [("0", "EXENTO"), ("1", "IVAG"), ("2", "IVAR"), ("3", "IVAL")]


class AccountTax(models.Model):
    _inherit = "account.tax"

    fiscal_type_sel = fields.Selection(
        selection=FISCAL_TYPE_SEL,
        string="Tipo de impuesto fiscal",
        default="0",
        required=True,
    )
