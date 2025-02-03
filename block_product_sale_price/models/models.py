# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends_context('uid')
    def _compute_can_set_price(self):
        self.can_set_price = self.env.user.has_group('block_product_sale_price.can_set_product_price')

    can_set_price = fields.Boolean(compute='_compute_can_set_price')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id')
    def _compute_can_set_price(self):
        for record in self:
            record.can_set_price = record.product_id.can_set_price

    can_set_price = fields.Boolean(compute='_compute_can_set_price')
