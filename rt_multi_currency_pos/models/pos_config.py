from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
class PosConfig(models.Model):
    _inherit = "pos.config"

    second_currency_id = fields.Many2one(related="company_id.second_currency_id")

    @api.constrains('pricelist_id', 'use_pricelist', 'available_pricelist_ids', 'journal_id', 'invoice_journal_id', 'payment_method_ids')
    def _check_currencies(self):
        for config in self:
            if config.use_pricelist and config.pricelist_id not in config.available_pricelist_ids:
                raise ValidationError(_("The default pricelist must be included in the available pricelists."))
