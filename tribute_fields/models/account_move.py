from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

CUSTOMER_DOCUMENTS = ['out_invoice','out_refund']
VENDOR_DOCUMENTS = ['in_invoice','in_refund']


class AccountMove(models.Model):
    _inherit = "account.move"

    control_number = fields.Char("Control Number", copy=False)
    fiscal_check = fields.Boolean("Is Fiscal", default=False, copy=False)
    fiscal_correlative = fields.Char("Fiscal Correlative", copy=False)

    @api.onchange('fiscal_check')
    def onchange_fiscal_check(self):

        def get_max_sequence(sequence_list):
            max_num = -1
            max_sequence = None
            for sequence in sequence_list:
                numbers = "".join(re.findall(r"\d+", sequence or ""))
                if numbers and int(numbers) > max_num:
                    max_num = int(numbers)
                    max_sequence = sequence
            return max_sequence

        def get_next_sequence(sequence):
            flag = True
            sequence_elements = re.split(r"(\d+)", sequence or "")
            sequence_elements.reverse()
            sequence_numbers = len([
                *filter(lambda e: e.isdigit(), sequence_elements)
            ])
            new_sequence = []
            for element in sequence_elements:
                if flag and element.isdigit():
                    sequence_numbers -= 1
                    element_len = len(element)
                    element = str(int(element) + 1).zfill(element_len)
                    flag = False
                    if element_len != len(element) and sequence_numbers:
                        element = "".zfill(element_len)
                        flag = True
                new_sequence.append(element)
            new_sequence.reverse()
            return "".join(new_sequence)

        if self.fiscal_check:
            if self.move_type in CUSTOMER_DOCUMENTS:
                moves = self.env['account.move'].search([
                    ('fiscal_check', '=', True),
                    ('move_type', '=', self.move_type),
                    ('company_id', '=', self.company_id.id),
                ])

                max_control_number = get_max_sequence(
                    moves.mapped("control_number"))
                max_fiscal_correlative = get_max_sequence(
                    moves.mapped("fiscal_correlative"))
                self.control_number = get_next_sequence(max_control_number)
                self.fiscal_correlative = get_next_sequence(max_fiscal_correlative)
        else:
            self.control_number = None
            self.fiscal_correlative = None

    @api.constrains("fiscal_correlative", "control_number")
    def _constrains_fiscal_fields(self):
        try:
            if self.fiscal_check:
                if self.move_type in CUSTOMER_DOCUMENTS:
                    moves = self.env['account.move'].search([
                        ('id', '!=', self.id),
                        ('move_type', '=', self.move_type),
                        ('fiscal_check', '=', self.fiscal_check),
                        '|',
                        ('control_number','!=',False),
                        ('fiscal_correlative', '!=', False),
                        '|',
                        ('control_number', '=', self.control_number),
                        ('fiscal_correlative', '=', self.fiscal_correlative),
                    ])

                    assert not moves, _(
                        "The fiscal correlative and the control number must be unique, check the following documents: %s" % moves.mapped(
                            "name")
                    )
            else:
                assert not (self.control_number or self.fiscal_correlative), _(
                    "The 'Control Number' and 'Fiscal Correlative' fields are only for fiscal invoices"
                )
        except Exception as e:
            raise UserError(str(e))
