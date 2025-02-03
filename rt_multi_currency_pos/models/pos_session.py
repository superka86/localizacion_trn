from odoo import api, models, fields

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        res = super()._pos_ui_models_to_load()
        res.append('second.currency')
        return res


    def _loader_params_product_product(self):
        res = super()._loader_params_product_product()
        res.get("search_params").get("fields").append("ref_list_price")
        return res


    def _get_pos_ui_second_currency(self, params):
        return self.env['res.currency'].search_read(**params['search_params'])[0]


    def _loader_params_second_currency(self):
        return {
            'search_params': {
                'domain': [('id', '=', self.config_id.second_currency_id.id)],
                'fields': ['name', 'symbol', 'position', 'rounding', 'rate', 'decimal_places'],
            },
        }

    def _loader_params_pos_payment_method(self):
        res = super()._loader_params_pos_payment_method()
        res.get("search_params").get("fields").append("currency_id")
        return res

    def _get_pos_ui_pos_payment_method(self, params):
        res = super()._get_pos_ui_pos_payment_method(params)
        for item in res:
            item["currency_id"] = self.env["res.currency"].search_read(**{
                "domain": [("id", "=", (item["currency_id"] and item["currency_id"][0]) or self.env.company.currency_id.id)],
                "fields": ["name", "symbol", "position", "rounding", "rate", "decimal_places"],
            })[0]
        return res

    def _create_combine_account_payment(self, payment_method, amounts, diff_amount):
        amounts['amount'] = self.company_id.currency_id._convert(
            from_amount=amounts['amount'],
            to_currency=payment_method.journal_id.currency_id,
            company=self.company_id,
            date=fields.Date.today(),
            round=True,
        )
        return super()._create_combine_account_payment(payment_method, amounts, diff_amount)

    def _create_split_account_payment(self, payment, amounts):
        amounts['amount'] = self.company_id.currency_id._convert(
            from_amount=amounts['amount'],
            to_currency=payment.payment_method_id.journal_id.currency_id,
            company=self.company_id,
            date=fields.Date.today(),
            round=True,
        )
        return super()._create_split_account_payment(payment, amounts)

    def get_closing_control_data(self):
        res = super().get_closing_control_data()
        payment_methods = res.get("other_payment_methods")
        currency_fields = ["name", "symbol", "position", "rounding", "rate", "decimal_places"]
        company_currency = self.env.company.currency_id.read(fields=currency_fields)
        for method in payment_methods:
            currency = self.env["pos.payment.method"].browse([method["id"]]).currency_id.read(fields=currency_fields)
            method["currency"] = currency and currency[0] or company_currency[0]

        return res