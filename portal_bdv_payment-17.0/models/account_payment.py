from datetime import timedelta

from odoo import fields, models, api, _, SUPERUSER_ID


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        self.ensure_one()
        if self.payment_transaction_id:
            date = self.payment_transaction_id.date - timedelta(hours=4)
            self.with_user(SUPERUSER_ID).move_id.write(
                {
                    'date': date.date(),
                    'invoice_date': date.date()
                }
            )
            self.with_user(SUPERUSER_ID).date = date.date()
        super(AccountPayment, self).action_post()
