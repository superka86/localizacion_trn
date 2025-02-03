from odoo import fields, api, models


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    iva_retention_journal_id = fields.Many2one(
        related="company_id.iva_retention_journal_id",
        domain="[('type','=','general')]",
        readonly=False,
    )
    islr_retention_journal_id = fields.Many2one(
        related="company_id.islr_retention_journal_id",
        domain="[('type','=','general')]",
        readonly=False,
    )
    iae_retention_journal_id = fields.Many2one(
        related="company_id.iae_retention_journal_id",
        domain="[('type','=','general')]",
        readonly=False,
    )
    iva_account_id = fields.Many2one(
        related="company_id.iva_account_id",
        readonly=False,
    )
    islr_account_id = fields.Many2one(
        related="company_id.islr_account_id",
        readonly=False,
    )
    iae_account_id = fields.Many2one(
        related="company_id.iae_account_id",
        readonly=False,
    )
    retention_signature = fields.Image(
        related="company_id.retention_signature", readonly=False
    )
    active_retention_theoretical = fields.Boolean(
        related="company_id.active_retention_theoretical", readonly=False
    )
