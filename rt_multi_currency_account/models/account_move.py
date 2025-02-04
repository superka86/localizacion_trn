from odoo import models, fields, api, _
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    second_currency_id = fields.Many2one(
        "res.currency",
        "Second Currency",
        default=lambda self: self.env.company.second_currency_id,
        domain='[("id", "!=", currency_id)]',
    )
    second_company_currency_id = fields.Many2one(
        string="Second Company Currency",
        related="company_id.second_currency_id",
    )
    second_amount_untaxed_signed = fields.Monetary(
        "Second Tax Excluded",
        currency_field="second_company_currency_id",
        compute="_compute_second_amounts",
    )
    second_amount_tax_signed = fields.Monetary(
        "Second Tax",
        currency_field="second_company_currency_id",
        compute="_compute_second_amounts",
    )
    second_amount_total_signed = fields.Monetary(
        "Second Total",
        currency_field="second_company_currency_id",
        compute="_compute_second_amounts",
    )
    second_amount_total_in_currency_signed = fields.Monetary(
        "Total in Second Currency",
        currency_field="second_currency_id",
        compute="_compute_second_amounts",
    )
    second_tax_totals = fields.Binary(
        compute="_compute_second_tax_totals", exportable=False
    )
    rate_string = fields.Char("Rate", compute="_compute_rate_string")
    second_currency_rate = fields.Char("Second Rate", compute="_compute_rate_string", exportable=False)
    show_second_currency_rate = fields.Boolean("Show Second Currency Rate", default=True)

    def _convert(self, amount, to_currency=None):
        self.ensure_one()
        if self.currency_id:
            return self.currency_id._convert(
                from_amount=amount,
                to_currency=to_currency or self.second_currency_id,
                company=self.company_id,
                date=self.date or fields.date.today(),
                round=True,
            )
        return amount


    @api.depends("currency_id", "second_currency_id", "date", "amount_total")
    def _compute_second_amounts(self):
        for move in self:
            move.second_amount_total_in_currency_signed = move._convert(
                move.amount_total
            )
            move.second_amount_untaxed_signed = move._convert(
                amount=move.amount_untaxed,
                to_currency=move.company_id.second_currency_id,
            )
            move.second_amount_tax_signed = move._convert(
                amount=move.amount_tax,
                to_currency=move.company_id.second_currency_id,
            )
            move.second_amount_total_signed = move._convert(
                amount=move.amount_total,
                to_currency=move.company_id.second_currency_id,
            )

    @api.depends("currency_id", "second_currency_id", "date")
    def _compute_rate_string(self):
        for move in self:
            rate_string = ""
            move.second_currency_rate = ""
            if move.currency_id and move.second_currency_id:
                rate = self.env["res.currency"]._get_conversion_rate(
                    from_currency=move.currency_id,
                    to_currency=move.second_currency_id,
                    company=move.company_id,
                    date=move.date or fields.date.today(),
                )
                inverse_rate = self.env["res.currency"]._get_conversion_rate(
                    from_currency=move.second_currency_id,
                    to_currency=move.currency_id,
                    company=move.company_id,
                    date=move.date or fields.date.today(),
                )

                rate_string = (
                    "("
                    + formatLang(self.env, 1, currency_obj=move.currency_id)
                    + " = "
                    + formatLang(
                        self.env, rate, currency_obj=move.second_currency_id
                    )
                    + ")"
                )
                report_rate = max([rate, inverse_rate])
                move.second_currency_rate = formatLang(self.env, report_rate,
                    currency_obj=move.currency_id if rate <= inverse_rate else move.second_currency_id
                    )
            move.rate_string = rate_string

    @api.depends("tax_totals", "second_currency_id", "date")
    def _compute_second_tax_totals(self):
        for move in self:
            ref_json = None
            if move.tax_totals:
                ref_json = {}
                tax_totals = move.tax_totals
                lang_env = self.with_context(lang=move.partner_id.lang).env
                converted_subtotals = []
                converted_subtotal_groups = {}

                for item in tax_totals["subtotals"]:
                    converted_subtotals += [
                        {
                            **item,
                            "amount": move._convert(item["amount"]),
                            "formatted_amount": formatLang(
                                lang_env,
                                move._convert(item["amount"]),
                                currency_obj=move.second_currency_id,
                            ),
                        }
                    ]

                for key, value in tax_totals["groups_by_subtotal"].items():
                    converted_subtotal_groups[key] = []
                    for tax in value:
                        converted_subtotal_groups[key].append(
                            {
                                **tax,
                                "tax_group_name": tax["tax_group_name"],
                                "tax_group_amount": move._convert(
                                    tax["tax_group_amount"]
                                ),
                                "tax_group_base_amount": move._convert(
                                    tax["tax_group_base_amount"]
                                ),
                                "formatted_tax_group_amount": formatLang(
                                    lang_env,
                                    move._convert(
                                        tax["tax_group_amount"],
                                    ),
                                    currency_obj=move.second_currency_id,
                                ),
                                "formatted_tax_group_base_amount": formatLang(
                                    lang_env,
                                    move._convert(
                                        tax["tax_group_base_amount"],
                                    ),
                                    currency_obj=move.second_currency_id,
                                ),
                            }
                        )

                converted_amounts = {
                    "amount_total": move._convert(
                        tax_totals["amount_total"],
                    ),
                    "amount_untaxed": move._convert(
                        tax_totals["amount_untaxed"],
                    ),
                    "groups_by_subtotal": converted_subtotal_groups,
                }

                ref_json.update(
                    {
                        **tax_totals,
                        **converted_amounts,
                        "subtotals": converted_subtotals,
                        "formatted_amount_total": formatLang(
                            lang_env,
                            converted_amounts["amount_total"],
                            currency_obj=move.second_currency_id,
                        ),
                        "formatted_amount_untaxed": formatLang(
                            lang_env,
                            converted_amounts["amount_untaxed"],
                            currency_obj=move.second_currency_id,
                        ),
                    }
                )

            move.second_tax_totals = ref_json
