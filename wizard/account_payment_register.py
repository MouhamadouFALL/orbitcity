# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    _description = 'Register Payment'


    so_code = fields.Char(string="Memo", store=True, readonly=False)