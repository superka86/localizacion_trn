# -*- coding: utf-8 -*-
import datetime
import logging
import threading

from requests.auth import HTTPBasicAuth
import requests

from odoo import models, fields, api, _, SUPERUSER_ID
from odoo import models, fields, api, _
from odoo.exceptions import UserError

from ..utils.bdv_utils import BDVUtils as BDV, RESPONSE_STATUS

_logger = logging.getLogger(__name__)

MESSAGES_STATUS = [
    _('Payment Pending'),
    _('Payment Processed'),
    _('Payment InProcess'),
    _('Payment Canceled')
]


def _verify_payment(records):
    for record in records:
        with record.pool.cursor() as full_trx:
            self_trx = record.with_env(record.env(cr=full_trx))
            full_trx = record.pool.cursor()
    
            rec = self_trx.sudo().search([('id', '=', record.id)])
            try:
                data_token = BDV.generate_token_auth(rec.provider_id)

                if data_token['error']:
                    raise ValueError(data_token['data']['message'])

                access_token = data_token['data']['access_token']
                response_bdv = BDV.get_payment(rec.provider_id, access_token, rec.provider_reference)

                transaction_vals = {}

                if response_bdv['error']:
                    _logger.info(response_bdv.reason)
                    continue

                payment_data = response_bdv['data']

                status_code = payment_data.get('status')
                response_code = payment_data.get('responseCode')

                if response_code == 0:
                    transaction_vals['state'] = RESPONSE_STATUS[status_code]
                else:
                    transaction_vals['state'] = 'error'
                    transaction_vals['state_message'] = payment_data.get('responseDescription')
                    rec.with_user(SUPERUSER_ID).write(transaction_vals)
                    _logger.info(rec.state_message)
                    continue
                transaction_vals['state_message'] = payment_data.get('responseDescription') if transaction_vals[
                                                                                                   'state'] == 'error' else \
                    MESSAGES_STATUS[status_code]
                rec.with_user(SUPERUSER_ID).write(transaction_vals)
                if rec.state == 'done':
                    payment = rec.env['account.payment'].sudo().search([('ref_payment', '=', rec.provider_reference),
                                                                        ('company_id', '=',
                                                                         rec.provider_id.company_id.id)],
                                                                       limit=1)
                    if payment:
                        if payment.state == 'draft':
                            payment.with_user(SUPERUSER_ID).action_post()
                        rec.payment_id = payment
                        rec.with_user(SUPERUSER_ID).state = 'done'
                    else:
                        rec.with_user(SUPERUSER_ID)._reconcile_after_done()
                    rec.with_user(SUPERUSER_ID).is_processed = True
                    for order in rec.sale_order_ids.filtered_domain([('state', 'not in', ['cancel', 'sale'])]):
                        order.with_user(SUPERUSER_ID).action_confirm()
                full_trx.commit()
            except Exception as e:
                full_trx.rollback()
                _logger.info(e)
            finally:
                full_trx.close()


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    payment_title = fields.Char()
    payment_description = fields.Char()
    letter = fields.Selection(
        [('V', 'V'), ('J', 'J'), ('E', 'E')],
    )
    payment_url = fields.Char()
    return_url = fields.Char()

    def _verify_payment_ipg(self, env):
        limit = self.env.ref('portal_bdv_payment.cron_limit_process_payments')
        diff_days = self.env.ref('portal_bdv_payment.cron_diff_days')
        domain = [('state', '!=', 'cancel'), ('state', '!=', 'done'),
                  ('provider_id.code', '=', 'bdv')]
        date_filter = datetime.datetime.now()
        one_day = datetime.timedelta(days=int(diff_days.value))
        yesterday = date_filter - one_day
        domain.append(('create_date', '>', yesterday))
        records = self.search(domain, limit=int(limit.value), order='create_date desc')
        transaction_thread = threading.Thread(target=_verify_payment, args=(records,))
        transaction_thread.start()

    def _cancel_old_sale_order(self):
        domain = [('state', 'not in', ['cancel', 'done']),
                  ('provider_id.code', '=', 'bdv')]
        date_filter = datetime.datetime.now()
        diff_days = self.env.ref('portal_bdv_payment.cron_diff_days')
        one_day = datetime.timedelta(days=int(diff_days.value))
        yesterday = date_filter - one_day

        domain.append(('create_date', '<', yesterday))

        for rec in self.search(domain):
            rec.state = 'cancel'
            for order in rec.sale_order_ids.filtered_domain([('state', 'not in', ['cancel', 'sale'])]):
                order.with_user(SUPERUSER_ID).action_cancel()

    def _reprocess_all_after_done_bdv(self, env):
        limit = env.ref('portal_bdv_payment.cron_limit_process_payments')
        recs = self.search([('state', '=', 'done'),
                            ('is_processed', '=', False),
                            ('provider_id.code', '=', 'bdv'),
                            ('payment_id', '=', False)
                            ], limit=int(limit.value))
        for rec in recs:
            try:
                payment = env['account.payment'].sudo().search([('ref_payment', '=', rec.provider_reference)])
                if payment:
                    if payment.state == 'draft':
                        payment.with_user(SUPERUSER_ID).action_post()
                    rec.payment_id = payment
                    rec.with_user(SUPERUSER_ID).state = 'done'
                else:
                    rec.with_user(SUPERUSER_ID)._reconcile_after_done()
                rec.with_user(SUPERUSER_ID).is_processed = True
            except Exception as e:
                rec.env.cr.rollback()
                _logger.exception("Transaction post processing failed: %s", str(e))
