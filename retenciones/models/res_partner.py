from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    iva_retention_tax_id = fields.Many2one(
        "retention.tax", "IVA Retention", domain='[("type","=","iva")]'
    )
