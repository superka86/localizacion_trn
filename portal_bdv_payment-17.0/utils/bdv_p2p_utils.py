import requests as r
import datetime
from odoo import _
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons.payment_acquirer_list.utils.payment_portal_utils import PaymentPortalUtils as Utils

HEADERS = {
    "Content-Type": "application/json",
}


class BDVP2PUtils:
    TEMPLATE_FORM = "portal_bdv_payment.bdv_p2p_payment_form"
    TEMPLATE_PROCESS = "portal_bdv_payment.process_payment_p2p"

    @staticmethod
    def get_banks():
        banks = []
        domain = [
            ('is_active', '=', True),
            ('code', '!=', False)
        ]
        bank_records = request.env['res.bank'].search(domain)

        for bank in bank_records:
            banks.append({
                'Code': bank.code,
                'Name': bank.name
            })

        if banks:
            banks = sorted(banks, key=lambda d: d['Code'])

        return banks

    @staticmethod
    def _validate_payment_config(payment_config):
        if not payment_config:
            raise UserError(_('Payment Config Is Required'))

        if not payment_config.url:
            raise UserError(_('URL Required for BDV P2P'))

        if not payment_config.receiver_phone:
            raise UserError(_('Receiver Phone Required for BDV P2P'))

        if not payment_config.api_key:
            raise UserError(_('Api Key Required for BDV P2P'))

    @staticmethod
    def validate_search_p2p(portal, post):
        payment_config = portal.get('payment_config')
        amount_total_currency = portal.get('amount_total_currency')

        BDVP2PUtils._validate_payment_config(payment_config)

        if not amount_total_currency:
            raise UserError(_("Amount Total Currency Is Required"))
        
        importe = "{:.2f}".format(float(amount_total_currency))
        
        data = {
            "cedulaPagador": post['dni'],
            "telefonoPagador": post['cellphone'],
            "telefonoDestino": payment_config.receiver_phone,
            "referencia": post['n_reference'],
            "fechaPago": str(post['payment_date']),
            "importe": importe,
            "bancoOrigen": post['bank']
        }
        

        response = BDVP2PUtils.execute_request_post(
            payment_config.url,
            data,
            payment_config.api_key
        )

        log = payment_config.save_log(portal, "validate_search_p2p - BDV", data, response)
        BDVP2PUtils.get_validate_response(response)
        return response['result']

    @staticmethod
    def get_validate_response(response):
        if response['error']:
            if 'data' in response['result']:
                raise UserError(response['result']['data'])

            raise UserError(response['result'])

        if 'code' not in response['result']:
            raise UserError(_('Error CODE BDV'))

        if 'data' not in response['result']:
            raise UserError(_('Error DATA BDV'))

        if response['result']['code'] != 1000:
            message_error = str(response['result']['code']) + ', ' + str(response['result']['message'])
            raise UserError(message_error)

    @staticmethod
    def get_validate_data(post):

        today = Utils.get_today()

        if 'bank' not in post:
            raise UserError(_("Bank Is Required"))

        if 'letter' not in post:
            raise UserError(_("Letter is Required"))

        if 'number' not in post:
            raise UserError(_("Number is Required"))

        if 'payment_date' not in post:
            raise UserError(_("Payment Date is Required"))

        if len(post.get('bank')) != 4:
            raise UserError(_("Bank Not Valid"))

        if len(post.get('letter')) != 1:
            raise UserError(_("Letter Not Valid"))

        if len(post.get('payment_date')) != 10:
            raise UserError(_("Payment Date Not Valid"))

        if post.get('letter') not in ['V', 'E', 'G', 'J']:
            raise UserError(_("Letter Not Valid"))

        try:
            post['number'] = int(post['number'])
            post['dni'] = post['letter'] + str(post['number'])
            post['n_reference'] = int(post['n_reference'])
            post['cellphone'] = Utils.replace_phone58(post['cellphone'])
            post['payment_date'] = datetime.datetime.strptime(post['payment_date'], '%Y-%m-%d').date()
        except Exception as e:
            raise UserError(e)
            # raise UserError(_("Invalid Fields"))

        if post['payment_date'] > today:
            raise UserError(_('Payment Date Not Valid'))

        if post['number'] < 9999:
            raise UserError(_('Vat Not Valid'))

    @staticmethod
    def execute_request_post(url, data, key):
        result = {'result': {}, 'error': True}
        headers = HEADERS
        headers['X-API-Key'] = key
        try:
            response = r.post(url, headers=HEADERS, json=data)
        except Exception as e:
            result['result']['message'] = e
            return result

        if not response.ok:
            result['result']['message'] = response.reason + ' , status code: ' + str(response.status_code)
            result['result']['code'] = str(response.status_code)
            return result

        result = {'result': response.json(), 'error': False}

        return result
