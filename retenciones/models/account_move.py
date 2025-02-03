from odoo import fields, api, models, _
from odoo.exceptions import UserError


IAE_TYPES = [("S", "Service"), ("C", "Purchase")]


class AccountMove(models.Model):
    _inherit = "account.move"

    retention_currency_id = fields.Many2one(
        "res.currency",
        "Retention Currency",
        default=lambda self: self.env["res.currency"].browse([3]),
    )
    islr_retention_tax_id = fields.Many2one(
        "retention.tax", "ISLR Retention", domain="[('type','=','islr')]"
    )
    iae_retention_tax_id = fields.Many2one(
        "retention.tax", "IAE Retention", domain="[('type','=','iae')]"
    )
    iva_retention_tax_id = fields.Many2one(
        related="partner_id.iva_retention_tax_id",
        domain="[('type','=','iva')]",
        readonly=False,
        store=True
    )

    iva_retention = fields.Monetary(
        "Amount detained by IVA",
        currency_field="retention_currency_id",
        compute="compute_retention_amount"
    )
    islr_retention = fields.Monetary(
        "Amount detained by ISLR",
        currency_field="retention_currency_id",
        compute="compute_retention_amount"
    )
    iae_retention = fields.Monetary(
        "Amount detained by IAE",
        currency_field="retention_currency_id",
        compute="compute_retention_amount"
    )
    total_detained = fields.Monetary(
        "Total detained",
        currency_field="retention_currency_id",
        compute="compute_retention_amount"
    )
    iae_type = fields.Selection(IAE_TYPES, "Transaction type")
    retention_line_id = fields.Many2one("retention.line", "Retention Line")
    is_active_theoretical = fields.Boolean(related="company_id.active_retention_theoretical")


    @api.depends(
        "amount_total",
        "currency_id",
        "retention_currency_id",
        "iva_retention_tax_id",
        "islr_retention_tax_id",
        "iae_retention_tax_id",
        "invoice_date",
    )
    def compute_retention_amount(self):
        for move in self:

            def _convert(amount):
                return move.currency_id._convert(
                    from_amount=amount,
                    to_currency=move.retention_currency_id,
                    company=move.company_id,
                    date=move.invoice_date or fields.date.today(),
                    round=True,
                )

            def _percentage(amount, percentage):
                return amount * percentage / 100

            lines_amount_untaxed = sum(
                move.invoice_line_ids.filtered_domain(
                    [("tax_ids.name", "ilike", "EXENTO")]
                ).mapped("price_total")
            )
            amount_base = move.amount_untaxed - lines_amount_untaxed
            taxes = {
                'iva': move.iva_retention_tax_id.tax,
                'islr': move.islr_retention_tax_id.tax,
                'iae': move.iae_retention_tax_id.tax,
            }

            iva_retention = _percentage(move.amount_tax, taxes['iva'])
            islr_retention = _percentage(amount_base, taxes['islr'])
            iae_retention = _percentage(amount_base, taxes['iae'])
            move.iva_retention = _convert(iva_retention)
            move.islr_retention = _convert(islr_retention)
            move.iae_retention = _convert(iae_retention)

            if move.islr_retention_tax_id.decrement:
                move.islr_retention -= (
                    move.islr_retention_tax_id.decrement
                )

            move.total_detained = (
                move.iva_retention
                + move.islr_retention
                + move.iae_retention
            )

    def create_retentions(self):
        RETENTION_DOMAIN = [
            ("partner_id", "=", self.partner_id.id),
            ("company_id", "=", self.company_id.id),
            ("current", "=", True),
            ("state", "=", "draft"),
        ]

        retention_types = {}

        if self.iva_retention_tax_id:
            retention_types["iva"] = {
                "tax": self.iva_retention_tax_id.id,
                "journal": self.company_id.iva_retention_journal_id.id,
            }

        if self.islr_retention_tax_id:
            retention_types["islr"] = {
                "tax": self.islr_retention_tax_id.id,
                "journal": self.company_id.islr_retention_journal_id.id,
            }

        if self.iae_retention_tax_id:
            retention_types["iae"] = {
                "tax": self.iae_retention_tax_id.id,
                "journal": self.company_id.iae_retention_journal_id.id,
            }

        currency = self.env["res.currency"].browse([3])

        for ret_type, value in retention_types.items():
            current_retention = self.env["retention"].search(
                RETENTION_DOMAIN + [("type", "=", ret_type)]
            )

            new_retention_line = self.env["retention.line"].create(
                {
                    "invoice_id": self.id,
                    "ret_tax_id": value["tax"],
                    "currency_id": currency.id
                }
            )

            if not current_retention:
                new_retention = self.env["retention"].create(
                    {
                        "company_id": self.company_id.id,
                        "partner_id": self.partner_id.id,
                        "journal_id": value["journal"],
                        "type": ret_type,
                        "line_ids": [(4, new_retention_line.id)],
                        "date": self.date,
                    }
                )
                new_retention.onchange_date_or_type()
            else:
                new_retention_line.retention_id = current_retention

            new_retention_line.onchange_invoice_or_currency()

        return True

    def action_generate_retention_report(self):
        retention_amounts = {}
        lines_amount_untaxed = sum(
            self.invoice_line_ids.filtered_domain(
                [("tax_ids.name", "ilike", "EXENTO")]
            ).mapped("price_total")
        )
        amount_base = self.amount_untaxed - lines_amount_untaxed

        if not self.invoice_date:
            raise UserError(
                _("Please, add the invoice date to generate the Theoretical")
            )

        if self.iva_retention_tax_id:
            retention_amounts["iva"] = (
                self.amount_tax * self.iva_retention_tax_id.tax
            ) / 100

        if self.islr_retention_tax_id:
            retention_amounts["islr"] = (
                amount_base * self.islr_retention_tax_id.tax
            ) / 100

        if self.iae_retention_tax_id:
            retention_amounts["iae"] = (
                amount_base * self.iae_retention_tax_id.tax
            ) / 100

        return {
            "name": _("Retention Theoretical"),
            "type": "ir.actions.act_window",
            "res_model": "account.move.retention.wizard",
            "view_mode": "form",
            "context": {
                **retention_amounts,
                "invoice_name": self.name,
                "move_currency_id": self.currency_id.id,
                "invoice_amount_due": self.amount_residual,
                "invoice_date": self.invoice_date.strftime("%Y-%m-%d"),
                "partner_id": self.partner_id.id,
            },
            "target": "new",
        }

