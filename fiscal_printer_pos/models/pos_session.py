from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        res = super()._loader_params_res_partner()
        return {
            **(res or {}),
            "search_params": {
                **(res or {}).get("search_params", {}),
                "fields": [
                    *(res or {}).get("search_params", {}).get("fields", []),
                    "ced_rif",
                ],
            },
        }
