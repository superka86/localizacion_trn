# -*- coding: utf-8 -*-
import logging

from odoo import http
from odoo.http import request, Response
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class PosController(http.Controller):
    @http.route("/fp3dv/get-invoices", auth="user", type="json")
    def get_invoices(self, debug=False, **kwargs):
        invoices = request.env["account.move"].tdv_fp_get_invoices(debug=debug)
        return invoices

    @http.route("/fp3dv/update-invoice", auth="user", type="json")
    def update_fiscal_invoice(self, invoice={}):
        move = None
        if invoice:
            move = request.env["account.move"].search(
                [("name", "like", invoice.get("name"))], limit=1
            )
            if move:
                move.update_fp_fiscal_info(
                    {
                        "ticket_ref": invoice.get("fiscalNumber"),
                        "cn_ticket_ref": invoice.get("creditNoteNumber"),
                        "num_report_z": invoice.get("zNumber"),
                        "fp_serial_num": invoice.get("machineSerial"),
                        "fp_serial_date": invoice.get("fiscalDate"),
                        "fp_state": "printed",
                    }
                )
                return {"message": "Se ha procesado con exito", "success": True}
            else:
                raise UserError("No se pudo encontrar el documento asociado")
        else:
            raise UserError("El formato recibido no es valido")
