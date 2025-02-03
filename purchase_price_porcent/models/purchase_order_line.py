
from odoo import fields, models, api
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    computed_product_sale_price = fields.Float(
        string='Precio de Venta', 
        compute='_compute_price', 
        inverse='_compute_porcent', 
        store=True)
    computed_sale_price_porcent = fields.Float(string='Porcentaje de Precio')
    product_standard_price = fields.Float(related='product_id.standard_price', readonly=True)
    product_list_price = fields.Float(related='product_id.list_price', readonly=True)
    product_current_profit_porcent = fields.Float(string='Current Profit %', compute='_compute_old_profit_porcent', store=True)

    @api.depends('product_standard_price', 'product_list_price')
    def _compute_old_profit_porcent(self):
        for record in self:
            if record.product_standard_price == 0 or record.product_list_price == 0:
                record.product_current_profit_porcent = 0
            else:
                record.product_current_profit_porcent = 100 - ((record.product_standard_price * 100) / record.product_list_price)

    @api.depends('price_unit', 'computed_sale_price_porcent')
    def _compute_price(self):
        for record in self:
            if record.computed_sale_price_porcent >= 100:
                record.computed_sale_price_porcent = 99
            if record.computed_sale_price_porcent < 0:
                raise UserError("El porcentaje no puede ser negativo")
            elif record.computed_sale_price_porcent == 0:
                record.computed_product_sale_price = record.price_unit
            else:
                record.computed_product_sale_price = (record.price_unit * 100) / (100 - record.computed_sale_price_porcent)
    

    @api.onchange('computed_product_sale_price')
    def _compute_porcent(self):
        for record in self:
            if record.computed_product_sale_price == 0:
                record.computed_sale_price_porcent = 0
            else:
                record.computed_sale_price_porcent = 100 - ((record.price_unit * 100) / record.computed_product_sale_price)