# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _, exceptions
from odoo.tools import float_compare
from datetime import timedelta

import logging

_logger = logging.getLogger(__name__)


class Preorder(models.Model):
    _description = 'Preorder Order'
    _inherit = 'sale.order'

    # commitment_date >> date de livraison prevue
    account_payment_ids = fields.One2many('account.payment', 'sale_id', string="Pay sale advanced", readonly=True)
    amount_residual = fields.Float(
        "Residual Amount",
        readonly=True,
        compute_sudo=True,
        compute='_compute_advance_payment',
        digits=(16, 2),
        store=True
    )
    amount_payed = fields.Float('Payed Amount', compute_sudo=True, compute='_compute_advance_payment', digits=(16, 2), store=False)
    payment_line_ids = fields.Many2many(
        "account.move.line",
        string="Payment move lines",
        compute_sudo=True,
        compute="_compute_advance_payment",
        store=True,
    )
    advance_payment_status = fields.Selection(
        selection=[
            ("not_paid", "Not Paid"),
            ("paid", "Paid"),
            ("partial", "Partially Paid"),
        ],
        store=True,
        readonly=True,
        copy=False,
        tracking=True,
        compute_sudo=True,
        compute="_compute_advance_payment",
    )

    payment_count = fields.Float(compute_sudo=True, compute="_compute_advance_payment")

    first_payment_date = fields.Date("Date du Premier Paiement", compute='_compute_reminder_dates', store=True) # date confirmate date_order
    second_payment_date = fields.Date("Date du Deuxième Paiement", compute='_compute_reminder_dates', store=True) # un mois avant livraison
    third_payment_date = fields.Date("Date du Troisième Paiement", compute='_compute_reminder_dates', store=True) # date livraison commitment_date

    first_payment_amount = fields.Float("1er amount", compute="_compute_order_data", digits=(16, 2), store=True) 
    second_payment_amount = fields.Float("2nd amount", compute="_compute_order_data", digits=(16, 2), store=True) 
    third_payment_amount = fields.Float("3rd amount", compute="_compute_order_data", digits=(16, 2), store=True)

    first_payment_state = fields.Boolean(string="1er Payment status", compute='_compute_order_data', default=False, store=True)
    second_payment_state = fields.Boolean(string="2nd Payment status", compute='_compute_order_data', default=False, store=True)
    third_payment_state = fields.Boolean(string="3rd Payment status", compute='_compute_order_data', default=False, store=True)

    invoices = fields.One2many('account.move', 'sale_id', string="Invoices Sale Order", readonly=True)

    @api.depends('order_line.invoice_lines')
    def _get_invoices(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for order in self:
            invoices = order.order_line.invoice_lines.move_id.filtered(lambda r: r.move_type in ('out_invoice', 'out_refund'))
            order.invoices = invoices

    def action_view_payments(self):
        payments = self.mapped("account_payment_ids")
        action_ref = 'account.action_account_payments'
        # action_ref = 'account.action_move_out_invoice_type'
        action = self.env['ir.actions.act_window']._for_xml_id(action_ref)
        action['domain'] = [('id', 'in', payments.ids), ('sale_id', '=', self.id)]
        action['context'] = {
            'default_partner_id': self.partner_id.id,
            'default_sale_id': self.id,
            'default_payment_type': 'inbound',
            'default_ref': self.name,
            'default_date': fields.Datetime.today(),
            }
        
        if self.amount_payed < self.first_payment_amount:
            action['context']['default_amount'] = self.first_payment_amount
        elif self.amount_payed < (self.first_payment_amount + self.second_payment_amount):
            action['context']['default_amount'] = self.second_payment_amount
        else:
            action['context']['default_amount'] = self.third_payment_amount

        return action

    @api.depends(
            'order_line.price_subtotal', 
            'order_line.price_tax', 
            'order_line.price_total', 
            'account_payment_ids', 
            'amount_residual'
    )
    def _compute_order_data(self):
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.is_downpayment)
            if order_lines:
                sale_amount_total = sum(order_lines.mapped('price_subtotal')) + sum(order_lines.mapped('price_tax'))
                # les montants des paiements
                amount1 = round(sale_amount_total * 0.3, 2)
                amount2 = round(sale_amount_total * 0.3, 2)
                amount3 = round(sale_amount_total * 0.4, 2)

                order.first_payment_amount = amount1
                order.second_payment_amount = amount2
                order.third_payment_amount = amount3

                payments_amount = sum(order.account_payment_ids.filtered(lambda x: x.state == 'posted').mapped('amount'))

                if payments_amount >= round(amount1):
                    order.first_payment_state = True
                else:
                    order.first_payment_state = False

                if payments_amount >= round(amount2 + amount1):
                    order.second_payment_state = True
                else:
                    order.second_payment_state = False

                if payments_amount >= order.amount_total and order.amount_residual <= 0:
                    order.third_payment_state = True
                else:
                    order.third_payment_state = False

            else:
                order.first_payment_amount = 0.0
                order.second_payment_amount = 0.0
                order.third_payment_amount = 0.0

                order.first_payment_state = False
                order.second_payment_state = False
                order.third_payment_state = False


    @api.depends('date_order', 'commitment_date')
    def _compute_reminder_dates(self):
        for order in self:
            if order.date_order and order.commitment_date:
                order.first_payment_date = order.date_order
                order.second_payment_date = order.commitment_date - timedelta(days=30)
                order.third_payment_date = order.commitment_date  # Date de Livraison
            else:
                order.first_payment_date = False
                order.second_payment_date = False
                order.third_payment_date = False

    @api.depends(
        'currency_id',
        'company_id',
        'amount_total',
        'account_payment_ids',
        'account_payment_ids.state',
        'account_payment_ids.move_id',
        'account_payment_ids.move_id.line_ids',
        'account_payment_ids.move_id.line_ids.date',
        'account_payment_ids.move_id.line_ids.debit',
        'account_payment_ids.move_id.line_ids.credit',
        'account_payment_ids.move_id.line_ids.currency_id',
        'account_payment_ids.move_id.line_ids.amount_currency',
        'invoice_ids.amount_residual'
    )
    def _compute_advance_payment(self):
        for order in self:
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.account_type == "asset_receivable"
                          and x.parent_state == "posted"
            )
            advance_amount = 0.0
            for line in mls:
                line_currency = line.currency_id or line.company_id.currency_id
                # Exclude reconciled pre-payments amount because once reconciled
                # the pre-payment will reduce invoice residual amount like any
                # other payment.
                line_amount = (
                    line.amount_residual_currency
                    if line.currency_id
                    else line.amount_residual
                )
                line_amount *= -1
                if line_currency != order.currency_id:
                    advance_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )
                else:
                    advance_amount += line_amount

            # Consider payments in related invoices.
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids:
                invoice_paid_amount += inv.amount_total - inv.amount_residual
            amount_residual = order.amount_total - advance_amount - invoice_paid_amount
            payment_state = "not_paid"
            if mls:
                has_due_amount = float_compare(
                    amount_residual, 0.0, precision_rounding=order.currency_id.rounding
                )
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"
            order.payment_line_ids = mls
            order.amount_payed = order.amount_total - order.amount_residual
            order.payment_count = len(order.payment_line_ids)
            order.amount_residual = amount_residual
            order.advance_payment_status = payment_state

    def action_confirm(self):
        res = super(Preorder, self).action_confirm()
        
        for order in self:
            if order.amount_residual <= 0:
                order.write({
                    'state': 'to_delivered'	
                })

        if self.type_sale == 'order':
            # date = fields.Datetime.now()
            # self._create_invoices(date).action_post()
            self.message_post(body="La commande a été confirmée avec succès.")
            return res
        
        if self.type_sale == 'preorder':
            dates = [self.first_payment_date, self.second_payment_date, self.third_payment_date]
            amounts = [self.first_payment_amount, self.second_payment_amount, self.third_payment_amount]
            self._create_advance_invoices(dates, amounts)
            self.message_post(body="La commande a été confirmée avec succès.")
            return res
        
    # @api.onchange('amount_residual')
    # def _onchange_state(self):
    #     if self.amount_residual <= 0:
    #         return self.write({ 'state': 'to_delivered' })

    def _create_advance_invoices(self, dates, amounts):
        for order in self:
            self.env['sale.advance.payment.inv'].create({
                'sale_order_ids': [(6, 0, order.ids)],
                'advance_payment_method': 'fixed',
                'fixed_amount': amounts[0],
            })._create_invoices(order, dates, amounts)

    @api.depends('invoices', 'invoice_ids')
    def check_invoices_paid(self):
        for order in self:
            for invoice in order.invoices:
                if invoice.payment_state != 'paid':
                    _logger.info(f"Status de paiements {invoice.payment_state}")
                    return False
        return True
    
    def action_to_delivered(self):
        for order in self:
            _logger.info(f"Status de paiements {order.check_invoices_paid()}")
            if order.type_sale == 'order':
                if order.amount_residual <= 0:
                    return order.write({ 'state': 'to_delivered' })  
                else:
                    raise exceptions.ValidationError(_("Veuillez effectuer les paiements"))
            if order.type_sale == 'preorder':
                if order.amount_residual <= 0 and order.advance_payment_status == 'paid':
                    return order.write({ 'state': 'to_delivered' })
                else:
                    raise exceptions.ValidationError(_("Veuillez effectuer les paiements"))
                
    # def action_to_delivered(self):
    #     for order in self:
    #         _logger.info(f"Status de paiements {order.check_invoices_paid()}")
    #         if order.type_sale == 'order':
    #             if order.amount_residual <= 0:
    #                 return order.write({ 'state': 'to_delivered' })  
    #             else:
    #                 raise exceptions.ValidationError(_("Veuillez effectuer les paiements"))
    #         if order.type_sale == 'preorder':
    #             if order.amount_residual <= 0 and order.advance_payment_status == 'paid':
    #                 return order.write({ 'state': 'to_delivered' })
    #             else:
    #                 raise exceptions.ValidationError(_("Veuillez effectuer les paiements"))

    @api.onchange('order_line.qty_delivered')
    def action_delivered(self):
        for order in self:
            undelivered_lines = order.order_line.filtered(lambda line: line.qty_delivered < line.product_uom_qty)
            if undelivered_lines:
                undelivered_produts = ", ".join(undelivered_lines.mapped('product_id.name'))
                raise exceptions.ValidationError(_("Veuillez effectuer la livraison des produits non livrés : {0}".format(undelivered_produts)))
            else:
               order._create_invoices()
               return order.write({'state': 'delivered'})
            
    def action_delivered_a(self):
        for order in self:
            undelivered_lines = order.order_line.filtered(lambda line: line.qty_delivered < line.product_uom_qty)
            if undelivered_lines and order.delivery_status != 'full':
                undelivered_produts = ", ".join(undelivered_lines.mapped('product_id.name'))
                raise exceptions.ValidationError(_("Veuillez effectuer la livraison des produits non livrés : {0}".format(undelivered_produts)))
            elif order.delivery_status == 'full':
               return order.write({ 'state': 'delivered' })
            

    # @api.depends('order_line.qty_delivered', 'order_line.product_uom_qty')
    # def _compute_delivery_status(self):
    #     for order in self:
    #         if all(line.qty_delivered >= line.product_uom_qty for line in order.order_line):
    #             order.write({
    #                 'state': 'delivered'	
    #             })
    #         elif order.state == 'sale' and order.amount_residual <= 0:
    #             order.write({
    #                 'state': 'to_delivered'	
    #             })

    #         _logger.info(f" Valeur dans state ==>  {order.state}  type de la valeur ==> {type(order.state)}")
    #         _logger.info(f" Valeur dans amount_residual ==> {order.amount_residual} type de la valeur ==> {order.amount_total}")
