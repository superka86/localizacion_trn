# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import datetime
from ..utils.bdv_utils import MESSAGES_STATUS, BDVUtils as BDV
from odoo import http, _, fields, SUPERUSER_ID
from odoo.http import request
from odoo.addons.ingeint_isp_control.controllers.base_portal_payments import BasePortalPayments

_logger = logging.getLogger(__name__)


class ControllerBdvPayment(BasePortalPayments):

    @http.route(['/bdv/payment'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def verify_payment(self, **post):
        values = {
            'error': {
                'error': "",
            },
            'error_message': []
        }
        company = request.env.company
        if request.env.user.login != 'public':
            partner = request.env.user.partner_id
        if request.env.user.login == 'public':
            request.env.su = True
        currency = request.env['res.currency'].sudo().search([('name', 'in', ['VES', 'VEF']),
                                                              ('rate_ids', '!=', False),
                                                              ('active', '=', True), ], limit=1)
        sale_order = False
        invoice = False
        amount_total_currency = 0.00
        title = ''
        description = ''
        payment_config = False
        today = fields.Date.today(request)

        if 'acquirer_id' in post:
            if post['acquirer_id'] != '':
                payment_config = request.env['payment.provider'].sudo().search([('id', '=', int(post['acquirer_id']))])

        if not payment_config and request.httprequest.method == 'GET':
            values.update({
                'error': {
                    _("Payment Error"): _("Payment Error")
                },
                'error_message': [_("Payment not configured")],
            })
            return request.render('portal_bdv_payment.bdv_payment_form', values)
        if 'title' in post:
            title = post['title']
        if 'description' in post:
            description = post['description']
        if 'amount_total_currency' in post:
            if post['amount_total_currency'] != '':
                amount_total_currency = float(post['amount_total_currency'])

        parameters = self._get_amount_payment(post)
        sale_order = parameters.get("sale_order")
        invoice = parameters.get("invoice")
        partner = parameters.get("partner")
        title = parameters.get("title")
        description = parameters.get("description")
        amount_total_currency = parameters.get("amount_total_currency")

        if 'invoice_id' not in post and 'order_id' not in post:
            values.update({
                'error': {
                    _("Payment Error"): _("Payment Error")
                },
                'error_message': [_("Missing Order or Invoice!")],
            })
            return request.render('portal_bdv_payment.bdv_payment_form', values)
        payment_transaction = request.env['payment.transaction']
        if sale_order:
            for trans in sale_order.sudo().transaction_ids.filtered(
                    lambda x: x.state not in ['cancel', 'done'] and x.amount == amount_total_currency):
                payment_transaction = trans
        elif invoice:
            for trans in invoice.sudo().transaction_ids.filtered(
                    lambda x: x.state not in ['cancel', 'done'] and x.amount == amount_total_currency):
                payment_transaction = trans
        if payment_transaction:
            reference = payment_transaction.reference
        elif request.httprequest.method == 'GET':
            reference = request.env['ir.sequence'].sudo().next_by_code('ipg') or 'New'
        else:
            reference = post['reference']
        number = ''
        for vat in partner.vat:
            if vat.isdigit():
                number += vat
        number = str(int(number))
        cellphone = partner.phone if partner.phone else partner.mobile
        if '+58' in cellphone:
            cellphone = cellphone.replace('+58', '0').replace(' ', '').replace('-', '')
        readonly_amount = True if sale_order or invoice else False
        values.update({
            'order_id': sale_order.id if sale_order else '',
            'invoice_id': invoice.id if invoice else '',
            'amount_total_currency': amount_total_currency,
            'number_id': number,
            'Cellphone': cellphone,
            'reference': reference,
            'page_name': 'bdv_payment',
            'default_url': '/bdv/payment',
            'current_date': datetime.now(),
            'error': {},
            'error_message': [],
            'readonly_amount': readonly_amount,
            'title': title,
            'description': description,
            'acquirer_id': payment_config.id,
        })

        if post and request.httprequest.method == 'POST':
            if not payment_config:
                payment_config = request.env['payment.acquirer'].sudo().search([('code', '=', 'bdv'),
                                                                                ('state', '!=', 'disabled'),
                                                                                ('company_id', '=', company.id)],
                                                                               limit=1)
            if not payment_config:
                values.update({
                    'error': {
                        _("Payment Error"): _("Payment Error")
                    },
                    'error_message': [_("Payment not configured")],
                })
                return request.render('portal_bdv_payment.bdv_payment_form', values)

            # BDV Integration
            url_base = request.env['ir.config_parameter'].get_param('web.base.url')

            data = {
                'currency': int(post['currency']),
                'amount': post['amount'],
                'title': post['title'],
                'description': post['description'],
                'reference': post['reference'],
                'letter': post['letter'],
                'number': post['number'],
                'cellphone': post['cellphone'],
                'email': partner.email,
                'urlToReturn': url_base + '/' + payment_config.url_to_return,
            }

            if not payment_transaction:
                # GET TOKEN - BDV - Integration

                data_token = BDV.generate_token_auth(payment_config)

                if data_token['error']:
                    return self.execute_message_error(values, data_token['data']['message'])

                access_token = data_token['data']['access_token']

                response = BDV.generate_payment(payment_config, access_token, data)

                if response['error']:
                    return self.execute_message_error(values, response['data']['message'])

            payment_data = False
            if not payment_transaction:

                payment_data = response['data']

                if payment_data.get('responseCode') != 0:
                    values.update({
                        "error": {
                            "responseCode": payment_data.get('responseCode')
                        },
                        "error_message": [payment_data.get('responseDescription')]
                    })
                    return request.render('portal_bdv_payment.bdv_payment_form', values)
            try:
                if not payment_transaction and payment_data:
                    if partner.country_id:
                        country_id = partner.country_id
                    else:
                        country = request.env.ref('base.ve')
                        partner.sudo().write({
                            'country_id': country.id
                        })
                        country_id = partner.country_id
                    transaction_vals = {
                        'provider_id': payment_config.id,
                        'provider_reference': payment_data.get('paymentId'),
                        'amount': data.get('amount'),
                        'partner_id': partner.id,
                        'partner_country_id': country_id.id,
                        'currency_id': currency.id,
                        'letter': data.get('letter'),
                        'payment_title': data.get('Title'),
                        'payment_description': data.get('description'),
                        'return_url': data.get('urlToReturn'),
                        'reference': data.get('reference'),
                        'payment_url': payment_data.get('urlPayment'),
                        'payment_method_id': payment_config.payment_method.id,
                        'currency_id': payment_config.currency_id.id,
                        'date': datetime.now(),
                    }
                    payment_transaction = payment_transaction.with_user(SUPERUSER_ID).create(transaction_vals)
                    if sale_order:
                        payment_transaction.with_user(SUPERUSER_ID).sale_order_ids = [(4, sale_order.id)]
                    elif invoice:
                        payment_transaction.with_user(SUPERUSER_ID).invoice_ids = [(4, invoice.id)]
                if sale_order:
                    sale_order.with_user(SUPERUSER_ID).state = 'sent'
                return request.redirect(payment_transaction.payment_url, local=False)
            except Exception as e:
                request.env.cr.rollback()
                values.update({
                    'error': {
                        'error': str(e),
                    },
                    'error_message': [str(e) + ' ' + traceback.format_exc()]
                })
                return request.render('portal_bdv_payment.bdv_payment_form', values)
        return request.render('portal_bdv_payment.bdv_payment_form', values)

    @http.route('/bdv/process_payment/', auth='public', website=True, methods=['GET', 'POST'])
    def process_payment(self, **kw):
        values = {
            'error': {
                'error': "",
            },
            'error_message': []
        }
        if 'cron' not in kw:
            values.update({
                'message_state': MESSAGES_STATUS[1],
                'state': _('done')
            })

            return request.render('portal_bdv_payment.process_payment', values)

    def execute_message_error(self, values, message):

        values.update({
            'error': {
                'error': message,
            },
            'error_message': [message]
        })
        return request.render('portal_bdv_payment.bdv_payment_form', values)
