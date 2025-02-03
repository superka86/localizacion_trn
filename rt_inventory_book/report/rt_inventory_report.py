from odoo import models


class rtInventoryReport(models.AbstractModel):
    _name = "report.rt_invetory_report.report"
    _inherit = "report.report_xlsx.abstract"
    _description = "Reporte de INventario"

    def generate_xlsx_report(self, workbook, data, report):
        row = 7
        start_date = report.start_date.strftime("%d/%m/%Y")
        end_date = report.end_date.strftime("%d/%m/%Y")
        sheet = workbook.add_worksheet("Inventario")
        header = workbook.add_format(
            {
                "bold": True,
                "bg_color": "#999999",
                "align": "center",
                "valign": "vcenter",
                "border": 1,
            }
        )
        border = workbook.add_format({"border": 1})
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
                "fg_color": "yellow",
            }
        )
        bold = workbook.add_format(
            {"bold": True, "border": 1, "align": "center", "valign": "vcenter"}
        )
        company_style = workbook.add_format(
            {
                "font_size": 16,
                "bold": True,
                "border": 1,
                "align": "center",
                "valign": "vcenter",
            }
        )
        sheet.merge_range("A1:C2", report.company_id.name, company_style)
        rif = report.company_id.vat or ""
        sheet.write(2, 0, f"RIF: {rif}", bold)
        sheet.write(3, 0, f"Moneda: {report.currency_id.name}", bold)
        sheet.merge_range("D3:G3", "Reporte de movimiento en unidades", bold)
        sheet.merge_range(
            "D4:G4", f"Desde Fecha: {start_date} Hasta Fecha: {end_date}", bold
        )
        sheet.merge_range("C7:E7", "Existencia Inicial", merge_format)
        sheet.merge_range("F7:G7", "Entradas", merge_format)
        sheet.merge_range("H7:I7", "Salidas", merge_format)
        sheet.merge_range("J7:K7", "Auto Consumo", merge_format)
        sheet.merge_range("L7:N7", "Existencia Final", merge_format)
        sheet.write(row, 0, "Descripcion", header)
        sheet.write(row, 1, "UdM", header)
        sheet.write(row, 2, "Cantidad", header)
        sheet.write(row, 3, "Costo Unit", header)
        sheet.write(row, 4, f"Monto ({report.currency_id.name})", header)
        sheet.write(row, 5, "Cantidad", header)
        sheet.write(row, 6, f"Monto ({report.currency_id.name})", header)
        sheet.write(row, 7, "Cantidad", header)
        sheet.write(row, 8, f"Monto ({report.currency_id.name})", header)
        sheet.write(row, 9, "Cantidad", header)
        sheet.write(row, 10, f"Monto ({report.currency_id.name})", header)
        sheet.write(row, 11, "Cantidad", header)
        sheet.write(row, 12, "Costo Unit", header)
        sheet.write(row, 13, f"Monto ({report.currency_id.name})", header)

        for line in report.inventory_line_ids:
            row += 1
            sheet.write(row, 0, line.product_id.name, border)
            sheet.write(row, 1, line.uom_id.name, border)
            sheet.write(row, 2, line.initial_amount_qty, border)
            sheet.write(row, 3, line.initial_cost, border)
            sheet.write(row, 4, line.initial_amount_qty * line.initial_cost, border)
            sheet.write(row, 5, line.total_purchased_qty, border)
            sheet.write(row, 6, line.total_purchased_amount, border)
            sheet.write(row, 7, line.total_sold_qty, border)
            sheet.write(row, 8, line.total_sold_amount, border)
            sheet.write(row, 9, line.self_consumption_qty, border)
            sheet.write(row, 10, line.self_consumption_amount, border)
            sheet.write(row, 11, line.final_amount_qty, border)
            sheet.write(row, 12, line.final_cost, border)
            sheet.write(row, 13, line.final_amount_qty * line.final_cost, border)

        sheet.set_column("A:A", 30)
        sheet.set_column("B:B", 10)
        sheet.set_column("C:N", 13)
