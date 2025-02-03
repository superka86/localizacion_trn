from odoo import models, api, fields

class AccountMoveRetentionWizard(models.TransientModel):

    _name = 'account.move.retention.wizard'
    _description = 'Wizard for the theoretical report of retentions'

    invoice_name = fields.Char('Bill', default=lambda self: self.env.context.get('invoice_name'))
    partner_id = fields.Many2one('res.partner', default=lambda self: self.env.context.get('partner_id'))
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.context.get('move_currency_id'))
    invoice_amount = fields.Monetary("Bill amount", currency_field='currency_id', default=lambda self: self.env.context.get('invoice_amount_due'))
    iva_retention_amount = fields.Monetary("IVA Retention", currency_field='currency_id', default=lambda self: self.env.context.get('iva'))
    islr_retention_amount = fields.Monetary("ISLR Retention", currency_field='currency_id', default=lambda self: self.env.context.get('islr'))
    iae_retention_amount = fields.Monetary("IAE Retention", currency_field='currency_id', default=lambda self: self.env.context.get('iae'))
    amount_total = fields.Monetary("Total to pay", currency_field='currency_id', compute='_compute_amount_total')

    ref_currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.currency'].browse([3]))
    ref_invoice_amount = fields.Monetary("Bill amount (Referential)", currency_field='ref_currency_id', compute='_compute_reference_amounts')
    ref_iva_retention_amount = fields.Monetary("IVA Retention (Referential)", currency_field='ref_currency_id', compute='_compute_reference_amounts')
    ref_islr_retention_amount = fields.Monetary("ISLR Retention (Referential)", currency_field='ref_currency_id', compute='_compute_reference_amounts')
    ref_iae_retention_amount = fields.Monetary("IAE Retention (Referential)", currency_field='ref_currency_id', compute='_compute_reference_amounts')
    ref_amount_total = fields.Monetary("Total to pay (Referential)", currency_field='ref_currency_id', compute='_compute_reference_amounts', readonly=True)

    invoice_date = fields.Date("Fecha", default=lambda self: self.env.context.get('invoice_date'))

    @api.depends('invoice_amount','iva_retention_amount','islr_retention_amount','iae_retention_amount')
    def _compute_amount_total(self):
        for wizard in self:
            wizard.amount_total = wizard.invoice_amount - (wizard.iva_retention_amount + wizard.islr_retention_amount + wizard.iae_retention_amount)


    @api.depends('currency_id','ref_currency_id','invoice_amount','iva_retention_amount','islr_retention_amount','iae_retention_amount')
    def _compute_reference_amounts(self):
        for wizard in self:
            wizard.ref_invoice_amount = wizard.currency_id._convert(wizard.invoice_amount, wizard.ref_currency_id, self.env.company, wizard.invoice_date, True)
            wizard.ref_iva_retention_amount = wizard.currency_id._convert(wizard.iva_retention_amount, wizard.ref_currency_id, self.env.company, wizard.invoice_date, True)
            wizard.ref_islr_retention_amount = wizard.currency_id._convert(wizard.islr_retention_amount, wizard.ref_currency_id, self.env.company, wizard.invoice_date, True)
            wizard.ref_iae_retention_amount = wizard.currency_id._convert(wizard.iae_retention_amount, wizard.ref_currency_id, self.env.company, wizard.invoice_date, True)
            wizard.ref_amount_total = wizard.currency_id._convert(wizard.amount_total, wizard.ref_currency_id, self.env.company, wizard.invoice_date, True)


    def print_report(self):
        # return self.env['ir.actions.report.xml'].render(
        #     'account.account.report_invoice',
        #     {
        #         'data': self.env['account.invoice'].browse(self.ids),
        #     }
        return self.env.ref('retenciones.action_account_move_retention_report').report_action(self)

