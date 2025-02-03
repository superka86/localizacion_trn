
from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_product_price_form(self):
        self.ensure_one()
        product_price = self.env['purchase.sale.price'].search(
            [('order_id', '=', self.id)], 
            limit=1
        )
        if not product_price:
            product_price = self.env['purchase.sale.price'].create({
                'name': self.name,
                'order_id': self.id,
                'order_line_ids': [
                    (4, line.id)
                    for line in self.order_line
                ]
            })

        return {
            'name': 'Productos',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.sale.price',
            'res_id': product_price.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }