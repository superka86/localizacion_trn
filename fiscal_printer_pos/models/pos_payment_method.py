from odoo import models, fields, api


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    fp_payment_method = fields.Selection(
        related='journal_id.fp_payment_method'
    )