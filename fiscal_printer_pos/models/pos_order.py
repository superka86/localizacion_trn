from odoo import models, fields, api
from odoo.exceptions import UserError


class PosOrder(models.Model):
    _inherit = 'pos.order'

    ticket_ref = fields.Integer(
        string='Referencia de ticket',
        help='Numero de ticket generado por la impresora fiscal',
        default=0
    )
    num_report_z = fields.Integer(
        string='Numero de Reporte Z',
        help='Numero actual de reporte Z, al cual pertenece la orden',
        default=0
    )
    fp_serial_num = fields.Char(
        string='Numero Serial FP',
        help='Numero serial de la impresora fiscal',
        default=''
    )
    fp_serial_date = fields.Char('Fecha de la factura fiscal', readonly=True)
    is_ticket_generated = fields.Boolean(
        string='Ticket Generado', compute='_compute_is_ticket_generated')

    @api.depends('account_move', 'account_move.ticket_ref')
    def _compute_is_ticket_generated(self):
        for record in self:
            move = record.account_move
            if move:
                record.is_ticket_generated = move.fp_state != 'none'
            else:
                record.is_ticket_generated = False

            if record.is_ticket_generated:
                record.ticket_ref = move.ticket_ref
                record.num_report_z = move.num_report_z
                record.fp_serial_num = move.fp_serial_num

    def send_to_fiscal_printer(self):
        self.ensure_one()
        if not self.ticket_ref and self.refunded_orders_count:
            refunded = self.refunded_order_ids[0]
            print(refunded)
            print(refunded.ticket_ref)
            
            if refunded:
                self.ticket_ref = refunded.ticket_ref
                self.num_report_z = refunded.num_report_z
                self.fp_serial_num = refunded.fp_serial_num
                self.fp_serial_date = refunded.fp_serial_date
        if not self.account_move:
            self.action_pos_order_invoice()
        self.account_move.send_to_fiscal_printer()
        return True

    def _prepare_invoice_vals(self):
        res = super()._prepare_invoice_vals()
        res.update({
            'ticket_ref': self.ticket_ref,
            'num_report_z': self.num_report_z,
            'fp_serial_num': self.fp_serial_num,
            'fp_serial_date': self.fp_serial_date
        })
        #Aqui van los datos de las facturas ya impresas
        return res
