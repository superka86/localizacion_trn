import requests
import json
from odoo import _

HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": authorization
}

HEADERS_IPG2 = {
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
}

MESSAGES_STATUS = [
    _('Payment Pending'),
    _('Payment Processed'),
    _('Payment InProcess'),
    _('Payment Canceled')
]

RESPONSE_STATUS = {
    0: 'pending',
    1: 'done',
    2: 'authorized',
    3: 'cancel',
}

GRAND_TYPE = "client_credentials"


class BDVUtils:
    @staticmethod
    def generate_token_auth(payment_config):

        result = {'data': {}, 'error': True}

        if not payment_config:
            result['data']['message'] = _('Payment Config Required')
            return result

        if not payment_config.user:
            result['data']['message'] = _('User BDV Required')
            return result

        if not payment_config.password:
            result['data']['message'] = _('Password BDV Required')
            return result

        data = {
            "grant_type": GRAND_TYPE,
            "client_id": payment_config.user,
            "client_secret": payment_config.password,
        }

        return BDVUtils.execute_request_post(payment_config.url_auth, HEADERS_IPG2, data, type="data")

    @staticmethod
    def generate_payment(payment_config, token, data):

        result = {'data': {}, 'error': True}

        if not payment_config:
            result['data']['message'] = _('Payment Config Required')
            return result

        if not token:
            result['data']['message'] = _('Token Required')
            return result

        headers = BDVUtils.generate_header_token(token)

        return BDVUtils.execute_request_post(payment_config.url, headers, data)

    @staticmethod
    def get_payment(payment_config, token, payment_token):

        result = {'data': {}, 'error': True}

        if not payment_config:
            result['data']['message'] = _('Payment Config Required')
            return result

        if not token:
            result['data']['message'] = _('Token Required')
            return result

        headers = BDVUtils.generate_header_token(token)
        url = '%s/%s' % (payment_config.url , payment_token)

        return BDVUtils.execute_request_get(  url , headers)

    @staticmethod
    def generate_header_token(token):
        headers = HEADERS
        headers['Authorization'] = 'Bearer %s' % token
        return headers

    @staticmethod
    def execute_request_post(url, headers, data, type="json"):
        result = {'data': {}, 'error': True}
        try:
            if type == "data":
                response = requests.post(url, headers=headers, data=data)
            elif type == "json":
                response = requests.post(url, headers=headers, json=data)
        except Exception as e:
            result['data']['message'] = e
            return result

        if not response.ok:
            result['data']['message'] = response.reason + ' , status code: ' + str(response.status_code)
            return result

        result = {'data': json.loads(response.text), 'error': False}

        return result

    @staticmethod
    def execute_request_get(url, headers):
        result = {'data': {}, 'error': True}
        try:
            response = requests.get(url , headers=headers, timeout=10)
        except Exception as e:
            result['data']['message'] = e
            return result

        if not response.ok:
            result['data']['message'] = response.reason + ' , status code: ' + str(response.status_code)
            return result

        result = {'data': json.loads(response.text), 'error': False}

        return result
