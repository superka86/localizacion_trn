from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    second_currency_id = fields.Many2one(
        related="company_id.second_currency_id", readonly=False
    )
    fixed_ref = fields.Boolean(
        "Fixed Currency", related="company_id.fixed_ref", readonly=False
    )
    product_cost_updatable = fields.Boolean(
        related="company_id.product_cost_updatable", readonly=False
    )

    def update_prices(self):
        products = self.env["product.template"].search([])

        def convert(product):
            if self.env.company.fixed_ref:
                product.list_price = self.env.company.second_currency_id._convert(
                    from_amount=product.ref_list_price,
                    to_currency=self.env.company.currency_id,
                    company=self.env.company,
                    date=self.env.company.second_currency_id.date,
                    round=True,
                )
                if self.product_cost_updatable:
                    product.standard_price = (
                        self.env.company.second_currency_id._convert(
                            from_amount=product.ref_standard_price,
                            to_currency=self.env.company.currency_id,
                            company=self.env.company,
                            date=self.env.company.second_currency_id.date,
                            round=True,
                        )
                    )

            else:
                product.ref_list_price = self.env.company.currency_id._convert(
                    from_amount=product.list_price,
                    to_currency=self.env.company.second_currency_id,
                    company=self.env.company,
                    date=self.env.company.second_currency_id.date,
                    round=True,
                )
                if self.product_cost_updatable:
                    product.ref_standard_price = self.env.company.currency_id._convert(
                        from_amount=product.standard_price,
                        to_currency=self.env.company.second_currency_id,
                        company=self.env.company,
                        date=self.env.company.second_currency_id.date,
                        round=True,
                    )

            product.ref_currency_id = self.env.company.second_currency_id

        products.mapped(convert)
