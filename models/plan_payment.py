#-*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date,timedelta


class PaymentPlan(models.Model):
    _name = "at.payment.plan"
    _description = "Management and reminder"

    name = fields.Char("Plan Name")
    start_date = fields.Date('Date confirm')
    end_date = fields.Date('Date shipping')
    reminder_date1 = fields.Date("Premiere date de rappel", store=True)
    reminder_date2 = fields.Date("Deuxieme date de rappel", store=True)
    reminder_date3 = fields.Date("Troisieme date de rappel", store=True)

    sale_order_id = fields.Many2one('sale.order', string="Bon de commande")

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