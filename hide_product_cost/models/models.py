# -*- coding: utf-8 -*-

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends_context('uid')
    def _compute_can_view_cost(self):
        self.can_view_cost = self.env.user.has_group('hide_product_cost.can_view_product_cost')

    can_view_cost = fields.Boolean(compute='_compute_can_view_cost')