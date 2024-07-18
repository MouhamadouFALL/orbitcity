#-*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date,timedelta


class PlanPaymentTrackLine(models.Model):
    _name = "plan.payment.track.line"
    _description = "Management and track line of payment client"

    name = fields.Char(string="track line payment")
    start_date = fields.Date('Date confirm')
    end_date = fields.Date('Date shipping')
    # reminder_date1 = fields.Date("Premiere date de rappel", store=True, compute='')
    # reminder_date2 = fields.Date("Deuxieme date de rappel", store=True)
    # reminder_date3 = fields.Date("Troisieme date de rappel", store=True)

    sale_order_id = fields.Many2one('sale.order', string="Bon de commande")

    f_date = fields.Date("Date 1er Paiement", related='sale_order_id.first_payment_date')
    s_date = fields.Date("Date 2eme Paiement", related='sale_order_id.second_payment_date')
    t_date = fields.Date("Date 3eme Paiement", related='sale_order_id.third_payment_date')

    amount1 = fields.Monetary("Versement 1er", related='sale_order_id.amount_date1')
    amount2 = fields.Monetary("Versement 2eme", related='sale_order_id.amount_date2')
    amount3 = fields.Monetary("Versement 3eme", related='sale_order_id.amount_date3')

    # deposit_invoice_ids = fields.Many2many(
    #     comodel_name='account.move',
    #     string="Facture Acompte",
    #     compute='_get_invoiced',
    #     search='_search_invoice_ids',
    #     copy=False)



    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoice_ids = invoices
            order.invoice_count = len(invoices)

    def _search_invoice_ids(self, operator, value):
        if operator == 'in' and value:
            self.env.cr.execute("""
                SELECT array_agg(so.id)
                    FROM sale_order so
                    JOIN sale_order_line sol ON sol.order_id = so.id
                    JOIN sale_order_line_invoice_rel soli_rel ON soli_rel.order_line_id = sol.id
                    JOIN account_move_line aml ON aml.id = soli_rel.invoice_line_id
                    JOIN account_move am ON am.id = aml.move_id
                WHERE
                    am.move_type in ('out_invoice', 'out_refund') AND
                    am.id = ANY(%s)
            """, (list(value),))
            so_ids = self.env.cr.fetchone()[0] or []
            return [('id', 'in', so_ids)]
        elif operator == '=' and not value:
            # special case for [('invoice_ids', '=', False)], i.e. "Invoices is not set"
            #
            # We cannot just search [('order_line.invoice_lines', '=', False)]
            # because it returns orders with uninvoiced lines, which is not
            # same "Invoices is not set" (some lines may have invoices and some
            # doesn't)
            #
            # A solution is making inverted search first ("orders with invoiced
            # lines") and then invert results ("get all other orders")
            #
            # Domain below returns subset of ('order_line.invoice_lines', '!=', False)
            order_ids = self._search([
                ('order_line.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund'))
            ])
            return [('id', 'not in', order_ids)]
        return [
            ('order_line.invoice_lines.move_id.move_type', 'in', ('out_invoice', 'out_refund')),
            ('order_line.invoice_lines.move_id', operator, value),
        ]


    # deposit_invoice_ids = fields.Many2many(
    #     comodel_name='account.move',
    #     string="Facture Acompte",
    #     compute='get_deposit_invoice_info',
    #     copy=False)




            # result = {
            #     'deposit_info': deposit_info,
            #     'ttl_paid': total_paid,
            #     'ttl_due': total_due,
            #     'ttl_amount': total_amount,
            #     'total_overdue': sum(inv.amount_residual for inv in deposit_invoices if inv.invoice_date_due and inv.invoice_date_due < fields.Date.today())
            # }
            #
            # return result

    # Example usage
    # sale_order = self.env['sale.order'].browse(sale_order_id)
    # deposit_invoice_info = sale_order.get_deposit_invoice_info()
    # print(deposit_invoice_info)

    # @api.depends('deposit_invoice_ids')
    # def _compute_deposit_totals(self):
    #     for order in self:
    #         total_paid = sum(line.amount_paid for line in order.deposit_invoice_ids)
    #         total_due = sum(line.amount_due for line in order.deposit_invoice_ids)
    #         total_amount = sum(line.invoice_total for line in order.deposit_invoice_ids)
    #         total_overdue = sum(line.amount_due for line in order.deposit_invoice_ids if
    #                             line.invoice_date and line.invoice_date < fields.Date.today())
    #
    #         order.total_paid = total_paid
    #         order.total_due = total_due
    #         order.total_amount = total_amount
    #         order.total_overdue = total_overdue

    # payment_amount_due = fields.Float("MT Du", compute='_compute_data')  # amount_due, amount_residual
    # payment_amount_overdue =fields.Float("MT en retart", compute='_compute_data')  # amount_overdue, amount_total

    @api.depends("sale_order_id")
    def _compute_data(self):
        for x in self:
            orders = x.mapped("sale_order_id")
            #invoices = orders.mapped("orders")
            for o in orders:
                x.start_date = o.date_order
                x.end_


    @api.onchange('start_date', 'end_date')
    def compute_reminder_dates(self):
        for payp in self:
            if payp.start_date and payp.end_date:
                period = payp.end_date - payp.start_date
                # part = period // 3
                part = period / 3
                payp.reminder_date1 = payp.start_date + part
                payp.reminder_date2 = payp.start_date + part + part
                #payp.reminder_date1 = payp.start_date + timedelta(days=period // 3)
                #payp.reminder_date2 = payp.start_date + timedelta(days=2 * (period // 3))
                # payp.reminder_date3 = payp.end_date - timedelta(days=5) # 5 jours avant la date du dernier paiement
                payp.reminder_date3 = payp.end_date  # Date de Livraison


    def send_payment_alert(self):
        for payp in self:
            today = fields.Date.today()
            for reminder_date in [payp.reminder_date1, payp.reminder_date2, payp.reminder_date3]:
                if today + timedelta(days=5) == reminder_date:
                    pass



