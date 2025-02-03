# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    code = fields.Selection(selection_add=[
        ('bdv', 'BDV'), ('bdv_p2p', 'BDV - P2P')
    ], ondelete={'bdv': 'set default', 'bdv_p2p': 'cascade'})
    user = fields.Char()
    password = fields.Char()
    url = fields.Char()
    url_to_return = fields.Char()
    url_auth = fields.Char()
    pricelist_id = fields.Many2one('product.pricelist')
    default_url = fields.Char()

    api_key = fields.Char()
    receiver_phone = fields.Char()
