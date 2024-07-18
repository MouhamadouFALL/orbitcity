#-*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_id = fields.Many2one(
        'sale.order',
        string='Sale',
        readonly=True,
        states={'draft': [("readonly", False)]}
    )

    def action_post(self):
        # Automatic reconciliation of payment when invoice confirmed.
        res = super(AccountMove, self).action_post()
        sale_order = self.mapped('line_ids.sale_line_ids.order_id')
        if sale_order and self.invoice_outstanding_credits_debits_widget is not False:
            json_invoice_outstanding_data = (
                self.invoice_outstanding_credits_debits_widget.get("content", [])
            )
            for data in json_invoice_outstanding_data:
                if data.get("move_id") in sale_order.account_payment_ids.move_id.ids:
                    self.js_assign_outstanding_line(line_id=data.get("id"))
        return res