# -*- coding: utf-8 -*-
import logging
from odoo import http, _, addons
from odoo.exceptions import UserError
from odoo.http import request
from ..utils.bdv_p2p_utils import BDVP2PUtils as bdv
from odoo.addons.payment_acquirer_list.controllers.base_portal import BasePortalPayments
from odoo.addons.payment_acquirer_list.utils.payment_portal_utils import PaymentPortalUtils as Utils

_logger = logging.getLogger(__name__)

class P2PController(BasePortalPayments):

    @http.route(['/bdv/p2p/payment'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def get_bdv_p2p_payment(self, **post):

        portal = {}
        try:
            self._validate_request_portal(post)
            portal = self._init_portal_payment(post)
            portal.update(provider='bdv_p2p')

            self._get_payment_provider(portal)

            parameters = self._get_amount_payment(post)
            partner = parameters.get("partner")

            portal.update(
                sale_order=parameters.get("sale_order"),
                invoice=parameters.get("invoice"),
                contract_aux_id=parameters.get('contract_aux_id'),
                company_id=parameters.get('company_id'),
                partner=partner,
                cellphone=Utils.get_cell_phone(partner),
                number=Utils.get_number_id(partner),
                title=parameters.get("title"),
                description=parameters.get("description"),
                amount_total_currency=parameters.get("amount_total_currency"),
                country_id=parameters.get('country_id'),
                page_name="bdv_p2p_payment",
                default_url="/bdv/p2p/payment",
                banks=bdv.get_banks(),
            )

            if self._get_debug_mode():
                portal.update(edit_amount=True)

            Utils.get_payment_transaction_portal(portal)

            if 'reference' in post:
                portal.update(reference=post["reference"])

            if portal.get('method') == 'GET':
                return request.render(bdv.TEMPLATE_FORM, portal)

            elif portal.get('method') == 'POST':

                bdv.get_validate_data(post)

                response = bdv.validate_search_p2p(portal, post)
                res_bdv = response['data']

                self._set_is_equal_amount(portal, res_bdv['amount'])

                data = self._set_data_payment(portal, post, {
                    'amount': res_bdv['amount']
                })

                reference_p2p = "BDV-P2P-" + str(post.get("n_reference"))

                transaction_vals = self._set_data_payment_transaction(reference_p2p, portal, data)

                self._validate_reference(portal, data={
                    'date': post['payment_date'],
                    'reference': post['n_reference'],
                    'amount': res_bdv['amount'],
                })

                self._create_payment_p2p(portal, transaction_vals)

                self._validate_equals_p2p(portal, data)

                return request.render(bdv.TEMPLATE_PROCESS, portal)

            else:
                raise UserError(_('Method not allow'))

        except Exception as e:
            request.env.cr.rollback()
            return self._execute_message_error(e, portal)
