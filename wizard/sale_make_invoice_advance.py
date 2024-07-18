
#-*- encoding: utf-8 -*-

from odoo import api, models, fields, _
from odoo.fields import Command

# class non utiliser
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    # @api.model
    # def _sale_ref(self):
    #     sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
    #     for x in sale_orders:
    #         self.sale_ref = x.name
    #
    # sale_ref = fields.Char(string="Ref SO")

    def _create_invoices(self, sale_orders, dates=None, amounts=None):
        self.ensure_one()

        if self.advance_payment_method == 'delivered':
            return sale_orders._create_invoices(final=self.deduct_down_payments)
        else:
            self.sale_order_ids.ensure_one()
            self = self.with_company(self.company_id)
            order = self.sale_order_ids

            invoices = []
            if dates and amounts:
                for i in range(3):  # Boucle pour créer 3 factures
                    # Créer le produit de dépôt si nécessaire
                    if not self.product_id:
                        self.product_id = self.env['product.product'].create(
                            self._prepare_down_payment_product_values()
                        )
                        self.env['ir.config_parameter'].sudo().set_param(
                            'sale.default_deposit_product_id', self.product_id.id)

                    # Créer la section de paiement anticipé si nécessaire
                    if not any(line.display_type and line.is_downpayment for line in order.order_line):
                        self.env['sale.order.line'].create(
                            self._prepare_down_payment_section_values(order)
                        )

                    down_payment_so_line = self.env['sale.order.line'].create(
                        self._prepare_so_line_values(order)
                    )

                    invoice = self.env['account.move'].sudo().create(
                        self._prepare_invoice_values(order, down_payment_so_line, dates[i], amounts[i])
                    ).with_user(self.env.uid)  # Unsudo the invoice after creation

                    invoice.message_post_with_view(
                        'mail.message_origin_link',
                        values={'self': invoice, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)

                    invoice.action_post()

                invoices.append(invoice)

            return invoices

    def _prepare_invoice_values(self, order, so_line, date, amount):
        self.ensure_one()
        return {
            **order._prepare_invoice(),
            'invoice_date': fields.Date.today(),
            'sale_id': order.id,
            'invoice_date_due': date,
            'invoice_line_ids': [
                Command.create(
                    so_line._prepare_invoice_line(
                        name=self._get_down_payment_description(order),
                        quantity=1.0,
                        price_unit=amount
                    )
                )
            ],
        }


    # def create_invoices(self):
    #     action = super(SaleAdvancePaymentInv, self).create_invoices()
    #     action['context']['default_sale_ref'] = self.sale_ref
    #
    #     return action


    # def _prepare_invoice_values(self, order, name, amount, so_line):
    #     res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
    #     res["sale_ref"] = order.name
    #
    #     return res

