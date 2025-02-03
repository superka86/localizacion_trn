from odoo import models, fields, api

RETENTION_TYPES = [
    ("iva", "IVA"),
    ("islr", "ISLR"),
    ("iae", "IAE"),
]


class RetentionTax(models.Model):
    _name = "retention.tax"
    _description = "Retention percentage applied"

    tax_name = fields.Char("Tax name", required=True)
    name = fields.Char("Name", compute="_compute_name")
    tax = fields.Float("Retention rate", required=True)
    code = fields.Char("Code", default="")
    type = fields.Selection(RETENTION_TYPES, "Retention type", required=True)
    decrement = fields.Monetary("Decrement (ISLR)", currency_field="currency_id")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        default=lambda self : self.env.company.currency_id
    )

    @api.depends("tax_name", "tax", "code", "type")
    def _compute_name(self):
        for record in self:
            record.name = (
                f"[{record.code}] {record.tax_name}"
                if record.code
                else record.tax_name or ""
            )
