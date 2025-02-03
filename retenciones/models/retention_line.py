from odoo import fields, api, models, _
from odoo.exceptions import UserError
import re

INVOICE_DOMAIN = """[
    ('company_id','=',company_id),
    ('move_type','in',['in_invoice','in_refund']),
    ('partner_id','=',partner_id),
    ('state','in',['posted','reversed']),
    ('id','not in', existing_invoice_ids)
]"""

IAE_TYPES = [
    ("none", ""),
    ("S", "Service"),
    ("C", "Purchase"),
]

REGISTRY_TYPES = [
    ("01", "01 - Invoice"),
    ("02", "02 - Debit Note"),
    ("03", "03 - Credit Note"),
]


class RetentionLine(models.Model):
    _name = "retention.line"
    _description = "Retention lines"

    retention_id = fields.Many2one("retention", "Retention")
    company_id = fields.Many2one(related="retention_id.company_id", store=True)
    state = fields.Selection(related="retention_id.state")
    type = fields.Selection(related="retention_id.type")
    partner_id = fields.Many2one(related="retention_id.partner_id", store=True)
    invoice_id = fields.Many2one(
        "account.move", "Bill", domain=INVOICE_DOMAIN, required=True
    )
    invoice_ref = fields.Char(related="invoice_id.fiscal_correlative", readonly=False)
    control_number = fields.Char(
        related="invoice_id.control_number",
        readonly=False,
    )
    registry_type = fields.Selection(REGISTRY_TYPES, "Registry Type")
    ret_tax_id = fields.Many2one(
        "retention.tax", "Retention Tax", domain="[('type','=',type)]"
    )
    currency_id = fields.Many2one(related="retention_id.currency_id")
    amount_base = fields.Monetary("Untaxed", currency_field="currency_id")
    amount_untaxed = fields.Monetary("Tax Free", currency_field="currency_id")
    amount_tax = fields.Monetary("Tax", currency_field="currency_id")
    amount_total = fields.Monetary("Total", currency_field="currency_id")
    amount_subtracting = fields.Monetary(
        "Subtracting",
        currency_field="currency_id",
        compute="_compute_amount_detained",
        store=True,
    )
    amount_detained = fields.Monetary(
        "Detained",
        currency_field="currency_id",
        compute="_compute_amount_detained",
        store=True,
    )
    credit_note_ids = fields.One2many(
        "account.move",
        "retention_line_id",
        related="invoice_id.reversal_move_id",
    )
    existing_invoice_ids = fields.Many2many(
        "account.move", compute="_compute_existing_invoice_ids"
    )
    iae_type = fields.Selection(
        related="invoice_id.iae_type", readonly=False, store=True
    )
    move_id = fields.Many2one("account.move", "Journal Entry")

    @api.depends("retention_id")
    def _compute_existing_invoice_ids(self):
        for line in self:
            line.existing_invoice_ids = line.retention_id.line_ids.invoice_id

    @api.onchange("invoice_id", "currency_id")
    def onchange_invoice_or_currency(self):

        def _convert(amount):
            return self.invoice_id.currency_id._convert(
                from_amount=amount,
                to_currency=self.currency_id,
                company=self.company_id,
                date=self.invoice_id.invoice_date,
                round=True
            )

        if self.invoice_id:
            lines_amount_untaxed = sum(
                self.invoice_id.invoice_line_ids.filtered_domain(
                    [("tax_ids.name", "ilike", "EXENTO")]
                ).mapped("price_total")
            )

            sign = 1 if self.invoice_id.move_type == "in_invoice" else -1

            self.amount_base = sign * \
                _convert((self.invoice_id.amount_untaxed - lines_amount_untaxed))
            self.amount_untaxed = sign * _convert(lines_amount_untaxed)
            self.amount_tax = sign * _convert(self.invoice_id.amount_tax)
            self.amount_total = sign * _convert(self.invoice_id.amount_total)

    @api.depends(
        "amount_base",
        "amount_untaxed",
        "amount_tax",
        "amount_total",
        "ret_tax_id",
        "retention_id.is_legal_entity",
    )
    def _compute_amount_detained(self):
        for line in self:

            def _percentage(amount):
                return amount * line.ret_tax_id.tax / 100

            line.amount_subtracting = line.ret_tax_id.currency_id._convert(
                from_amount=line.ret_tax_id.decrement,
                to_currency=line.currency_id,
                company=line.company_id or self.env.company,
                date=line.retention_id.date or fields.date.today(),
                round=True
            )

            line.amount_detained = _percentage(
                line.amount_base
                if line.retention_id.type != "iva"
                else line.amount_tax
            )

            if line.type == "islr" and not line.retention_id.is_legal_entity:
                sign = -1 if line.invoice_id.move_type == "in_invoice" else 1

                line.amount_detained += (sign * line.amount_subtracting) \
                    if line.amount_detained > line.amount_subtracting \
                    else (-line.amount_detained)

    def _get_move_lines_data(self, credit_account, debit_account, currency):

        def _convert(amount, currency=None):
            return self.currency_id._convert(
                from_amount=amount,
                to_currency=currency or self.company_id.currency_id,
                company=self.company_id,
                date=self.retention_id.date,
                round=True
            )

        amount_currency = _convert(abs(self.amount_detained), currency)
        balance = _convert(abs(self.amount_detained))

        debit_line = {
            "account_id": debit_account.id,
            "partner_id": self.partner_id.id,
            "currency_id": currency.id,
            "amount_currency": amount_currency,
            "debit": balance,
        }

        credit_line = {
            "account_id": credit_account.id,
            "partner_id": self.partner_id.id,
            "currency_id": currency.id,
            "amount_currency": -amount_currency,
            "credit": balance,
        }

        return debit_line, credit_line

    def _create_account_move(self):
        credit_account = (
            self.retention_id.credit_account_id
            or self.company_id._get_retention_account_id(self.type)
        )
        debit_account = (
            self.retention_id.debit_account_id
            or self.partner_id.property_account_payable_id
        )
        currency = self.retention_id.journal_currency or self.currency_id

        if self.amount_detained < 0:
            credit_account, debit_account = debit_account, credit_account

        if not self.move_id:
            self.move_id = self.env["account.move"].create(
                {
                    "ref": _(
                        "%s retention on %s (%s)"
                        % (
                            self.type.upper(),
                            self.invoice_id.name,
                            self.retention_id.name,
                        )
                    ),
                    "company_id": self.company_id.id,
                    "journal_id": self.retention_id.journal_id.id,
                    "currency_id": currency.id,
                    "date": self.retention_id.date,
                    "partner_id": self.partner_id.id,
                    "line_ids": [
                        (0, 0, line)
                        for line in self._get_move_lines_data(
                            credit_account, debit_account, currency
                        )
                    ],
                }
            )

        self.move_id.action_post()
        return True

    def _cancel_move(self):
        self.move_id.button_cancel()
        return True

    def _draft_move(self):
        self.move_id.button_draft()
        return True

    def get_text_info(self):
        if self.type == "iva":
            text_format = "\t".join(
                [
                    re.sub(
                        "[\-_.,#\\\]",
                        "",
                        self.retention_id.company_id.company_registry
                        or self.retention_id.company_id.vat,
                    ),
                    self.retention_id.period[:-2],
                    self.invoice_id.invoice_date.strftime("%Y-%m-%d"),
                    "C",
                    "01" if self.invoice_id.move_type == "in_invoice" else "03",
                    re.sub(
                        "[\-_.,#\\\]",
                        "",
                        self.retention_id.partner_id.vat
                        or self.retention_id.partner_id.ced_rif,
                    ),
                    re.sub("[\-_.,#\\\]", "", self.invoice_ref),
                    re.sub("[\_.,#\\\]", "", self.control_number),
                    str(abs(self.amount_total)),
                    str(abs(self.amount_base)),
                    str(abs(self.amount_detained)),
                    "0"
                    if not self.credit_note_ids
                    else re.sub(
                        "[\-_.,#\\\/]", "", self.credit_note_ids[0].name
                    ),
                    self.retention_id.correlative,
                    str(abs(self.amount_untaxed)),
                    "16",
                    "0",
                ]
            )
        else:
            text_format = "\t".join(
                [
                    self.retention_id.company_id.taxpayer_license,
                    self.retention_id.company_id.company_registry
                    or self.retention_id.company_id.vat,
                    self.retention_id.period[:4],
                    self.retention_id.period[4:6],
                    self.retention_id.partner_id.vat
                    or self.retention_id.partner_id.ced_rif,
                    self.iae_type,
                    self.retention_id.date.strftime("%d/%m/%Y"),
                    re.sub("[\-_.,#\\\]", "", self.invoice_ref),
                    re.sub("[\_.,#\\\]", "", self.control_number),
                    "FT" if not self.credit_note_ids else "NC",
                    self.retention_id.partner_id.taxpayer_license,
                    "NA"
                    if not self.credit_note_ids
                    else self.credit_note_ids[0].name,
                    "NA",
                    self.retention_id.correlative,
                    str(abs(self.amount_base)),
                    str(abs(self.ret_tax_id.tax)),
                    self.ret_tax_id.code,
                    str(abs(self.amount_detained)),
                    re.sub("[\-_.,#\\\]", "",
                           self.retention_id.partner_id.ruc),
                ]
            )

        return text_format
