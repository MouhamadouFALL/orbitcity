# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, tools, SUPERUSER_ID
from datetime import timedelta


class SaleOrderPaymentPlan(models.Model):
    _name = 'sale.order.payment.plan'
    _description = 'Plan de Paiement de la Commande'

    name = fields.Char("Name", required=True)
    client = fields.Many2one(
        comodel_name='res.partner',
        string="Client",
        required=True, readonly=False, index=True, change_default=True,
        tracking=1,
        domain="[('sale_order_ids.type_sale', 'in', ('preorder', 'creditorder'))]")
    sale_order_id = fields.Many2one('sale.order', string='Commande', domain="[('partner_id.sale_order_ids.type_sale', 'in', ('preorder', 'creditorder'))]")

    @api.model
    def _get_date_options(self):
        # Exemple: calculer 3 dates futures basées sur la date actuelle
        today = fields.Date.today()
        date1 = today + timedelta(days=60)  # 60 jours à partir d'aujourd'hui
        date2 = today + timedelta(days=90)  # 90 jours à partir d'aujourd'hui
        date3 = today + timedelta(days=120)  # 120 jours à partir d'aujourd'hui

        # Retourner un tuple de tuples pour la sélection
        return [
            ('date1', date1.strftime("%d/%m/%Y")),
            ('date2', date2.strftime("%d/%m/%Y")),
            ('date3', date3.strftime("%d/%m/%Y")),
        ]

        # return [
        #     ('date1', '05/04/2024'),
        #     ('date2', '05/05/2024'),
        #     ('date3', '05/06/2024'),
        # ]

    dates = fields.Selection(
        selection=_get_date_options,
        string="Dates",
    )


    # @api.model
    # @api.depends('sale_order_id.order_line.price_subtotal', 'sale_order_id.order_line.price_tax',
    #              'sale_order_id.order_line.price_total')
    # def _get_amount_date(self):
    #
    #     amount_date1 = None
    #     amount_date2 = None
    #     amount_date3 = None
    #
    #     for sopp in self:
    #         order_lines = sopp.sale_order_id.order_line.filtered(lambda x: not x.display_type)
    #         amount_total = sum(order_lines.mapped('price_subtotal')) + sum(order_lines.mapped('price_tax'))
    #         amount_date1 = round(amount_total * 0.3, 2)
    #         amount_date2 = round(amount_total * 0.3, 2)
    #         amount_date3 = round(amount_total * 0.4, 2)
    #
    #     print(amount_date1)
    #     return [
    #         ('amount_date1', amount_date1),
    #         ('amount_date2', amount_date2),
    #         ('amount_date3', amount_date3)
    #     ]
    #
    # @api.model
    # @api.depends('sale_order_id.date_order', 'sale_order_id.expiration_date')
    # def _get_date_options(self):
    #
    #     date_options = [('none', 'Aucune')]
    #     if self.sale_order_id:
    #         date_order = self.sale_order_id.date_order
    #         expiration_date = self.sale_order_id.expiration_date
    #         if date_order and expiration_date:
    #             date1 = date_order
    #             date2 = expiration_date - timedelta(days=30)
    #             date3 = expiration_date  # Date de Livraison
    #             date_options = [
    #                 ('date1', date1.strftime("%d/%m/%Y")),
    #                 ('date2', date2.strftime("%d/%m/%Y")),
    #                 ('date3', date3.strftime("%d/%m/%Y")),
    #             ]
    #     return date_options

    amount_remaining = fields.Float("Montant Restant", compute='_get_amount_payment')
    payment_date = fields.Datetime(string='Date Échéance')
    payment_amount = fields.Float(string='Montant à Verser')
    payed_amount = fields.Float("Montant Payé ")
    payment_status = fields.Selection([
        ('paid', 'Payé'),
        ('partial', 'partiel'),
        ('unpaid', 'Non Payé')
    ], string='Statut de Paiement', default='unpaid')

    @api.depends("sale_order_id")
    def _get_amount_payment(self):
        for sopp in self:
            sopp.amount_remaining = sopp.payment_amount - sopp.payed_amount

    @api.depends('sale_order_id.order_line')
    def _compute_payment_amount(self):
        for sopp in self:
            order_lines = sopp.sale_order_id.order_line.filtered(lambda x: not x.display_type)
            amount_total = sum(order_lines.mapped('price_subtotal')) + sum(order_lines.mapped('price_tax'))
            # Exemple de calcul, ajustez selon vos besoins
            sopp.payment_amount = round(amount_total * 0.3, 2)  # Juste un exemple

