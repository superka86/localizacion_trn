# -*- coding: utf-8 -*-

from odoo import fields, models


class InventoryResume(models.Model):
    _name = "rt.inventory.resume"
    _description = "resumen de inventario"

    name = fields.Char(string="name", required=True, readonly=True)
    description = fields.Char(string="description")

    start_date = fields.Date(string="start date", required=True, readonly=True)
    end_date = fields.Date(string="end date", required=True, readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
    )
    inventory_line_ids = fields.One2many(
        comodel_name="rt.inventory.resume.line",
        inverse_name="inventory_resume_id",
        string="lines",
    )

    company_id = fields.Many2one(
        string="company",
        comodel_name="res.company",
        default=lambda self: self.env.company.id,
    )

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
    )

    def unlink(self):
        for record in self:
            record.inventory_line_ids.unlink()
        return super().unlink()

    def generate_info(self):
        products = self.env["product.product"].search(
            [
                ("detailed_type", "=", "product"),
                "|",
                ("company_id", "=", self.company_id.id),
                ("company_id", "=", False),
            ]
        )
        report_lines = []
        for product in products:
            line_ids = self.env["account.move.line"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    # ("date", ">=", self.start_date),
                    ("date", "<=", self.end_date),
                    ("move_id.state", "=", "posted"),
                    ("product_id", "=", product.id),
                    (
                        "move_id.move_type",
                        "in",
                        ["in_invoice", "in_refund", "out_invoice", "out_refund"],
                    ),
                ]
            )
            ## Initial stock
            history_qty = 0
            history_amount = 0
            data = {
                "product_id": product.id,
                "initial_amount_qty": product.with_context(
                    {"to_date": self.start_date}
                ).qty_available,
                "final_amount_qty": product.with_context(
                    {"to_date": self.end_date}
                ).qty_available,
                "total_purchased_qty": 0,
                "total_purchased_amount": 0,
                "total_sold_qty": 0,
                "total_sold_amount": 0,
            }

            for line in line_ids:
                qty = line.product_uom_id._compute_quantity(
                    line.quantity, product.uom_id
                )
                amount = line.currency_id._convert(
                    line.price_unit,
                    self.currency_id,
                    self.company_id,
                    line.move_id.invoice_date,
                )
                if (
                    line.date < self.start_date
                    and line.move_id.move_type == "in_invoice"
                ):
                    history_amount += qty * amount
                    history_qty += qty
                    continue
                if line.date < self.start_date:
                    continue
                if line.move_id.move_type == "in_invoice":
                    data["total_purchased_qty"] += qty
                    data["total_purchased_amount"] += qty * amount
                elif line.move_id.move_type == "in_refund":
                    data["total_purchased_qty"] -= qty
                    data["total_purchased_amount"] -= qty * amount
                elif line.move_id.move_type == "out_invoice":
                    data["total_sold_qty"] += qty
                    data["total_sold_amount"] += qty * amount
                elif line.move_id.move_type == "out_refund":
                    data["total_sold_qty"] -= qty
                    data["total_sold_amount"] -= qty * amount
            data["initial_cost"] = history_amount / (history_qty or 1)
            data["final_cost"] = (history_amount + data["total_purchased_amount"]) / (
                (history_qty + data["total_purchased_qty"]) or 1
            )
            line = self.inventory_line_ids.filtered(
                lambda x: x.product_id.id == product.id
            )
            if (
                data["initial_amount_qty"]
                or data["final_amount_qty"]
                or data["total_sold_qty"]
                or data["total_purchased_qty"]
            ):
                if line:
                    line[0].write(data)
                else:
                    report_lines.append(data)
            elif line:
                line[0].unlink()
        if len(report_lines):
            self.inventory_line_ids = [(0, 0, line) for line in report_lines]
