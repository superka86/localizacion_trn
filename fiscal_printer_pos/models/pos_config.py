from odoo import fields, api, models


class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    default_customer_id = fields.Many2one('res.partner', string='Default Customer')
    fiscal_auto_print = fields.Boolean('Imprimir Automaticamente')

