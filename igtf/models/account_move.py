from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import formatLang
import json


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_igtf = fields.Monetary(
        "IGTF",
        compute="_compute_amount_igtf",
        currency_field="company_currency_id",
    )

    def _get_igtf_amount_in_currency(self, currency=None):
        amount_igtf = 0
        payments = self._get_reconciled_payments()
        amount_igtf += sum(
            payments.mapped(
                lambda p: p.currency_id._convert(
                    from_amount=p.igtf_tax,
                    to_currency=currency or self.currency_id,
                    company=self.company_id,
                    date=fields.datetime.now(),
                    round=True,
                )
            )
        )
        return amount_igtf

    @api.depends("amount_residual")
    def _compute_amount_igtf(self):
        for move in self:
            move.amount_igtf = move._get_igtf_amount_in_currency(
                move.company_currency_id
            )

    @api.depends(
        "line_ids.tax_base_amount",
        "line_ids.amount_currency",
        "partner_id",
        "line_ids.tax_line_id",
        "currency_id",
        "amount_total",
        "amount_untaxed",
        "line_ids.amount_residual",
    )
    def _compute_tax_totals(self):
        super()._compute_tax_totals()

        for invoice in self:
            widget = invoice.tax_totals
            if widget:
                amount_igtf = invoice._get_igtf_amount_in_currency()
                lang_env = self.with_context(lang=invoice.partner_id.lang).env

                amount_payments = sum(
                    invoice._get_reconciled_payments()
                    .filtered("is_igtf")
                    .mapped(
                        lambda payment: payment.currency_id._convert(
                            from_amount=payment.amount,
                            to_currency=invoice.currency_id,
                            company=invoice.company_id,
                            date=fields.datetime.now(),
                            round=True,
                        )
                    )
                )

                if amount_igtf:
                    aux_key = _("Untaxed Amount")
                    groups_by_subtotal = widget["groups_by_subtotal"]
                    groups_by_subtotal = {
                        **groups_by_subtotal,
                        aux_key: groups_by_subtotal.get(aux_key, [])
                        + [
                            {
                                "tax_group_name": "IGTF 3%",
                                "tax_group_amount": amount_igtf,
                                "tax_group_base_amount": amount_payments,
                                "formatted_tax_group_amount": formatLang(
                                    lang_env,
                                    amount_igtf,
                                    currency_obj=invoice.currency_id,
                                ),
                                "formatted_tax_group_base_amount": formatLang(
                                    lang_env,
                                    amount_payments,
                                    currency_obj=invoice.currency_id,
                                ),
                            }
                        ],
                    }

                    widget.update(
                        {
                            "amount_total": widget["amount_total"]
                            + amount_igtf,
                            "formatted_amount_total": formatLang(
                                lang_env,
                                widget["amount_total"] + amount_igtf,
                                currency_obj=invoice.currency_id,
                            ),
                            "groups_by_subtotal": groups_by_subtotal,
                        }
                    )
            invoice.tax_totals = widget

    @api.depends("move_type", "line_ids.amount_residual")
    def _compute_payments_widget_reconciled_info(self):
        super()._compute_payments_widget_reconciled_info()
        for move in self:
            igtf_move_ids = self.env["account.move"]
            payments_with_igtf = move._get_reconciled_payments().filtered(
                "is_igtf"
            )

            if move.invoice_payments_widget:
                for payment in payments_with_igtf:
                    igtf_move_ids |= self.env["account.move"].search(
                        [
                            ("invoice_origin", "=", payment.name),
                            ("company_id", "=", move.company_id.id),
                        ]
                    )

                widget = move.invoice_payments_widget

                if igtf_move_ids:
                    if widget and widget["content"]:
                        widget["content"] += [
                            {
                                "name": "IGTF payment",
                                "journal_name": ", ".join(
                                    igtf_move_ids.journal_id.mapped("name")
                                ),
                                "amount": sum(
                                    igtf_move_ids.mapped(
                                        lambda mv: mv.currency_id._convert(
                                            from_amount=mv.amount_total,
                                            to_currency=move.currency_id,
                                            company=move.company_id,
                                            date=fields.datetime.now(),
                                            round=True,
                                        )
                                    )
                                ),
                                "currency_id": move.currency_id.id,
                                "digits": [69, 2],
                                "position": move.currency_id.position,
                                "date": fields.datetime.now().strftime(
                                    "%Y-%m-%d"
                                ),
                                "ref": "Recargo por IGTF sobre "
                                + ", ".join(payments_with_igtf.mapped("name")),
                                "move_id": igtf_move_ids.mapped("id"),
                                "journal_ids": igtf_move_ids.mapped(
                                    "journal_id.id"
                                ),
                                "is_igtf": True,
                                "is_exchange": False,
                            }
                        ]

                move.invoice_payments_widget = widget

    def action_register_payment(self):
        res = super().action_register_payment()
        amount_residual = sum(
            self.mapped(
                lambda m: m.currency_id._convert(
                    from_amount=m.amount_residual,
                    to_currency=self.env.company.currency_id,
                    company=self.env.company,
                    date=fields.date.today(),
                    round=True,
                )
            )
        )

        res["context"].update(
            {
                "move_type": set(self.mapped("move_type")).pop(),
                "active_amount": amount_residual,
            }
        )

        return res
