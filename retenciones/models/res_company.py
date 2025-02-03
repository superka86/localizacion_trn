from odoo import fields, api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    iva_retention_journal_id = fields.Many2one(
        "account.journal",
        "IVA Retention Journal",
        domain="[('type','=','general')]",
    )
    islr_retention_journal_id = fields.Many2one(
        "account.journal",
        "ISLR Retention Journal",
        domain="[('type','=','general')]",
    )
    iae_retention_journal_id = fields.Many2one(
        "account.journal",
        "IAE Retention Journal",
        domain="[('type','=','general')]",
    )
    iva_account_id = fields.Many2one("account.account", "IVA Retention Account")
    islr_account_id = fields.Many2one(
        "account.account", "ISLR Retention Account"
    )
    iae_account_id = fields.Many2one("account.account", "IAE Retention Account")
    retention_signature = fields.Image("Retention Signature")
    active_retention_theoretical = fields.Boolean(
        "Activate theoretical", default=False
    )

    def _get_retention_account_id(self, ret_type):
        ret_accounts = {
            "iva": self.iva_account_id,
            "islr": self.islr_account_id,
            "iae": self.iae_account_id,
        }

        return ret_accounts[ret_type]

    def _get_retention_journal_id(self, ret_type):
        retention_journals = {
            "iva": self.iva_retention_journal_id,
            "islr": self.islr_retention_journal_id,
            "iae": self.iae_retention_journal_id,
        }

        return retention_journals[ret_type]


    def _get_full_address(self):
        field_list = self._get_company_address_field_names()
        address_info = []

        for key in field_list:
            val = (
                self[key]
                if key not in ("state_id", "country_id")
                else self[key].name
            )
            address_info.append(val if val else "")

        return " ".join(address_info)
