from odoo import fields, models


class MonthlyResumeWizard(models.TransientModel):
    _name = "rt.monthly.resume.wizard"
    _description = "wizard"

    name = fields.Char(string="name", required=True)
    start_date = fields.Datetime(string="start date", required=True)
    end_date = fields.Datetime(string="end date", required=True)

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )

    def confirm_action(self):
        record = self.env["rt.inventory.resume"].create(
            {
                "name": self.name,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "currency_id": self.currency_id.id,
            }
        )
        record.generate_info()

        return {
            "type": "ir.actions.act_window",
            "name": self.name,
            "res_model": "rt.inventory.resume",
            "res_id": record.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "current",
        }
