#-*- coding: utf8 -*-
from odoo import api, models, fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_result(self):
        # res = {}
        # for aml in self:
        #     res[aml.id] = aml.debit - aml.credit
        # return res

        for aml in self:
            aml.result = aml.debit - aml.credit



