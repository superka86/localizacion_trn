
from odoo import fields, models
from odoo.exceptions import UserError

class PurchaseSalePrice(models.Model):
    _name = 'purchase.sale.price'
    _description = '...'

    name = fields.Char(string='Especificacion')
    order_id = fields.Many2one('purchase.order', required=True)

    general_porcent = fields.Float(string='Porcentaje general', default=0)
    

    order_line_ids = fields.Many2many('purchase.order.line')

    def update_general_porcent(self):
        self.ensure_one()

        if self.general_porcent >= 100 or self.general_porcent < 0:
            raise UserError('El porcentaje debe estar en el rango [0, 100)')

        for line in self.order_line_ids:
            line.computed_sale_price_porcent = self.general_porcent

        return {
            'name': 'Productos',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.sale.price',
            'res_id': self.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    def validate_form(self):
        self.ensure_one()
        
        for line in self.order_line_ids:
            line.product_id.list_price = line.computed_product_sale_price