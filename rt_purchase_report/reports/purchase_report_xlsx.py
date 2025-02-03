from odoo import models
from odoo.tools.misc import format_amount
import re

STYLES = {
    "border": {
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    },
    "header": {
        "bold": True,
        "bg_color": "#999999",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    },
    "bold": {
        "bold": True,
        "bg_color": "#999999",
        "align": "center",
        "valign": "vcenter",
        "border": 1,
    },
    "merge_format": {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "yellow",
    },
    "merge_format1": {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "green",
    },
    "merge_format2": {
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "red",
    },
    "company_style": {
        "font_size": 16,
        "bold": True,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
    }
}

MOVE_TYPE = {
    False: "",
    "01": "01 - Factura",
    "02": "02 - Nota de débito",
    "03": "03 - Nota de crédito",
}

class PurchaseReportXlsx(models.AbstractModel):
    _name = 'report.rt_purchase_report.purchase_report_xlsx'
    _description = 'Report XLSX'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, report):

        def amount_format(amount,):
            return format_amount(self.env, amount, report.currency_id)

        def get_numbers(reference):
            numbers = re.findall(r'\d+', reference or "")
            return [int(number) for number in numbers]

        border = workbook.add_format(STYLES["border"])
        header = workbook.add_format(STYLES["header"])
        bold = workbook.add_format(STYLES["bold"])
        merge_format = workbook.add_format(STYLES["merge_format"])
        merge_format1 = workbook.add_format(STYLES["merge_format1"])
        merge_format2 = workbook.add_format(STYLES["merge_format2"])
        company_style = workbook.add_format(STYLES["company_style"])

        row = 7
        col = 9
        line_number = 0
        start_date = report.date_from.strftime("%d/%m/%Y")
        end_date = report.date_to.strftime("%d/%m/%Y")
        company_address = report.company_id.partner_id.contact_address or ""
        company_vat = report.company_id.company_registry or report.company_id.vat or ""

        sheet = workbook.add_worksheet(report.name)
        sheet.merge_range("A1:D2", report.company_id.name, company_style)
        sheet.merge_range("A3:G3", company_address, border)
        sheet.merge_range("A4:B4", "RIF: %s" % company_vat, bold)
        sheet.merge_range("C4:D4", "Periodo: %s - %s" %(start_date, end_date), bold)

        for tax in report.tax_totals.keys():
            sheet.merge_range(row-1, col, row-1, col+2, tax, merge_format)
            col += 3

        sheet.merge_range(row-1, col, row-1, col+3, "Retencion de IVA", merge_format)

        col = 9
        sheet.write(row, 0, "N°", header)
        sheet.write(row, 1, "Fecha de Factura", header)
        sheet.write(row, 2, "Cliente", header)
        sheet.write(row, 3, "RIF", header)
        sheet.write(row, 4, "Numero de Factura", header)
        sheet.write(row, 5, "Numero de Control", header)
        sheet.write(row, 6, "Tipo de Documento", header)
        sheet.write(row, 7, "Sin credito fiscal", header)
        sheet.write(row, 8, "Total", header)

        for e in range(len(report.tax_totals)):
            sheet.write(row, col, "Base Imponible", header)
            sheet.write(row, col + 1, "Alicuota", header)
            sheet.write(row, col + 2, "Total", header)
            col += 3

        sheet.write(row, col, "N° Comprobante", header)
        sheet.write(row, col+1, "Fecha", header)
        sheet.write(row, col+2, "Porcentaje", header)
        sheet.write(row, col+3, "Monto", header)

        for line in report.line_ids:

            row += 1
            line_number += 1
            col = 9
            sheet.write(row, 0, line_number, border)
            sheet.write(row, 1, line.invoice_date.strftime(
                "%d/%m/%Y") or "", border)
            sheet.write(row, 2, line.partner_id.name, border)
            sheet.write(row, 3, line.partner_id.vat or "", border)
            sheet.write(row, 4, line.invoice_reference or "", border)
            sheet.write(row, 5, line.control_number or "", border)
            sheet.write(row, 6, MOVE_TYPE[line.invoice_type], border)
            sheet.write(row, 7, amount_format(line.amount_exempt), border)
            sheet.write(row, 8, amount_format(line.amount_total), border)

            for tax_name in report.tax_totals.keys():
                tax = list(filter(lambda t: t["name"] == tax_name, line.tax_totals["taxes"]))
                if tax:
                    tax = tax.pop()
                    sheet.write(row, col, amount_format(tax["amount_untaxed"]), border)
                    sheet.write(row, col+1, "%s%%" %tax["tax"], border)
                    sheet.write(row, col+2, amount_format(tax["amount_tax"]), border)
                else:
                    sheet.write(row, col, amount_format(0), border)
                    sheet.write(row, col+1, amount_format(0), border)
                    sheet.write(row, col+2, amount_format(0), border)
                col += 3

            col = 9 + len(report.tax_totals) * 3
            sheet.write(row, col, line.retention_id.correlative or "", border)
            sheet.write(row, col+1, line.retention_id.date.strftime("%d/%m/%Y")
                if line.retention_id and line.retention_id.date
                else "", border
            )

            # ====== FIXME: WTF? Mrc que hiciste aquí? ========
            sheet.write(row, col+2, f"{line.retention_line_id.ret_tax_id.tax} %"
                if line.retention_line_id and line.retention_line_id.ret_tax_id
                else "", border
                )
            # ==================================================

            sheet.write(row, col+3, amount_format(line.amount_detained), border)

        row += 5
        sheet.write(row, 7, "Resumen del Libro", header)
        sheet.write(row, 8, "Total", header)
        row += 1

        if report.tax_totals:
            for tax, amount in report.tax_totals.items():
                sheet.write(row, 7, "%s" %tax, border)
                sheet.write(row, 8, amount_format(amount), border)
                row += 1

        sheet.write(row, 7, "Base Imponible", border)
        sheet.write(row+1, 7, "Sin credito fiscal", border)
        sheet.write(row+2, 7, "Impuestos", border)
        sheet.write(row+3, 7, "Total", border)
        sheet.write(row, 8, amount_format(report.amount_untaxed), border)
        sheet.write(row+1, 8, amount_format(report.amount_exempt), border)
        sheet.write(row+2, 8, amount_format(report.amount_tax), border)
        sheet.write(row+3, 8, amount_format(report.amount_total), border)


        sheet.set_column("A:A", 5)
        sheet.set_column("B:AZ", 25)
