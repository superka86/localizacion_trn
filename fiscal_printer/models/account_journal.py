from odoo import models, api, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    fp_payment_method = fields.Selection(
        string="Tipo de metodo",
        selection=[
            ("m1", "EFECTIVO"),
            ("m2", "DIVISAS"),
            ("m3", "TARJ/DEBITO"),
            ("m4", "TARJ/CREDITO"),
            ("m5", "Tranf en Bs"),
            ("m10", "Pago movil"),
            ("m11", "CREDITO"),
            # ('m6', 'EFECTIVO DIVISA (IGTF)'),
            # ('m7', 'MEDIOS DIGITALES (IGTF)'),
            # ('m8', 'TRANSFERENCIA DIVISAS (IGTF)'),
            # ('m9', 'OTROS (IGTF)'),
        ],
        default="m1",
    )
