# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from collections import defaultdict

PURCHASE_TYPE = [
    ("all", "All"),
    ("fiscal", "Control number"),
    ("no_fiscal", "No control number"),
]


class PurchaseReport(models.Model):
    _name = "rt.purchase.report"
    _description = "Purchase Report"

    name = fields.Char("Name", required=True)
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To", required=True)
    purchase_type = fields.Selection(
        PURCHASE_TYPE, "Purchase Type", default="all"
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
    line_ids = fields.One2many(
        "rt.purchase.report.line", "purchase_report_id", "Purchase Book Lines")
    amount_untaxed = fields.Monetary(
        "Amount Untaxed",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True)
    amount_exempt = fields.Monetary(
        "Exempt Amount",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True)
    amount_tax = fields.Monetary(
        "Taxes",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True)
    amount_total = fields.Monetary(
        "Total",
        currency_field="currency_id",
        compute="_compute_amounts",
        store=True)
    tax_totals = fields.Binary("Tax Totals", compute="_compute_tax_totals")

    @api.depends(
        "currency_id",
        "line_ids",
        "line_ids.amount_untaxed",
        "line_ids.amount_exempt",
        "line_ids.amount_tax",
        "line_ids.amount_total")
    def _compute_amounts(self):
        for book in self:
            book.amount_untaxed = sum(book.line_ids.mapped("amount_untaxed"))
            book.amount_exempt = sum(book.line_ids.mapped("amount_exempt"))
            book.amount_tax = sum(book.line_ids.mapped("amount_tax"))
            book.amount_total = sum(book.line_ids.mapped("amount_total"))

    @api.depends(
        "currency_id",
        "line_ids",
        "line_ids.amount_untaxed",
        "line_ids.amount_exempt",
        "line_ids.amount_tax",
        "line_ids.amount_total")
    def _compute_tax_totals(self):
        for book in self:
            tax_totals = defaultdict(int)
            tax_list = book.line_ids.mapped(lambda l: l.tax_totals["taxes"])

            for taxes in tax_list:
                for tax in taxes:
                    tax_totals[tax["name"]] += tax["amount_tax"]

            book.tax_totals = tax_totals


    @api.onchange("currency_id")
    def _onchange_currency_id(self):
        self.line_ids.mapped(lambda line: line.onchange_invoice_or_currency())

    def generate(self):
        domain = [
            ("company_id", "=", self.company_id.id),
            ("move_type", "in", ["in_invoice", "in_refund"]),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            ("state", "=", "posted"),
        ]

        if self.purchase_type != "all":
            domain.append(
                ("control_number", "!=", False)
                if self.purchase_type == "fiscal"
                else ("control_number", "=", False)
            )

        line_invoices = self.line_ids.invoice_id.filtered_domain(domain)
        self.line_ids.filtered(
            lambda line: line.invoice_id not in line_invoices
        ).unlink()
        invoices = self.env["account.move"].search(domain) - line_invoices
        new_lines = self.env["rt.purchase.report.line"].create(
            [
                {
                    "purchase_report_id": self.id,
                    "currency_id": self.currency_id.id,
                    "company_id": self.company_id.id,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                    "invoice_id": invoice.id,
                }
                for invoice in invoices
            ]
        )

        if new_lines:
            new_lines.mapped(lambda line: line.onchange_invoice_or_currency())

    @api.constrains("date_to", "date_from")
    def _constrains_date(self):
        for book in self:
            if not (book.date_from and book.date_to):
                raise UserError(_("The dates are required for registration"))
