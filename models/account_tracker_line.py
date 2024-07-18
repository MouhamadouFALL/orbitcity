# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from datetime import datetime, timedelta
from dateutil import relativedelta


class TrackerLine(models.Model):
    _name = "account.tracker.line"
    _description = "Follow-up creterial"
    _order = "delay asc"

    @api.model
    def _get_default_template(self):
        # try:
        #     return self.env.ref("orbit.email_template_account_tracker_default").id
        # except ValueError:
        #     return False

        # VERSION AMELIORER
        default_template = self.env.ref("orbit.email_template_account_tracker_default",
                                        raise_if_not_found=False)
        return default_template.id if default_template else False

    name = fields.Char("Action de suivi", required=True)
    user_id = fields.Many2one(comodel_name='res.users', string='User', readonly='False', copy=False,
                              default=lambda self: self.env.user)
    manual_action_responsible_id = fields.Many2one("res.users", "Assign a Responsible", default=lambda self: self.env.user, ondelete="set null")
    client = fields.Many2one(
        comodel_name='res.partner',
        string="Client",
        required=True, readonly=False, index=True, change_default=True,
        tracking=1,
        domain="[('sale_order_ids.type_sale', 'in', ('preorder', 'creditorder'))]")
    sale_order_id = fields.Many2one('sale.order', string="Numero commande", domain="[('partner_id', '=', client), ('partner_id.sale_order_ids.type_sale', 'in', ('preorder', 'creditorder'))]")
    currency_id = fields.Many2one(related='sale_order_id.currency_id')
    amount_to_paid = fields.Monetary(related='sale_order_id.amount_total', string="MT total")
    shipping_date = fields.Date(related='sale_order_id.expiration_date', string="Livraison prevue")
    due_date = fields.Date("Date Echeance", store=True, compute="_get_due_date")
    amount_paid = fields.Float("Montant payé", compute='_get_amount_payment')
    amount_remaining = fields.Float("Montant Restant", compute='_get_amount_payment')
    sequence = fields.Integer("Sequence", help="Gives the sequence order when displaying a list of follow-up lines.")
    delay = fields.Integer("Jours echeance", required=True,
                           help="The number of days after the due date of the invoice to wait before sending the reminder.  Could be negative if you want to send a polite alert beforehand.")
    # tracker_id = fields.Many2one('account.tracker', 'Follow Ups', required=True, ondelete="cascade")
    status = fields.Text('Statut')
    description = fields.Text("Message imprime", translate=True, default=""" 
    Dear %(partner_name)s,

    Exception made if there was a mistake of ours, it seems that the following amount stays unpaid. Please, take appropriate measures in order to carry out this payment in the next 8 days.

    Would your payment have been carried out after this mail was sent, please ignore this message. Do not hesitate to contact our accounting department. 

    Best Regards, """)

    send_email = fields.Boolean("Send an email", default=False, help="When processing, it will send an email")
    send_letter = fields.Boolean("Send a Letter", default=False, help="When processing, it will print a letter")
    manual_action = fields.Boolean("Manual Action", default=False, help="When processing, it will set the manual action to be taken for that customer.")
    manual_action_note = fields.Text("Action to Do", placeholder="e.g. Give a phone call, check with others , ...")
    email_template_id = fields.Many2one("mail.template", "Email template", defaut=_get_default_template,
                                        ondelete="set null")
    is_responsible = fields.Boolean("Est Responsable de la precommande", compute="_nb_relance")
    nb_relance= fields.Integer("Nombre de relance", default=0)

    first_payment_date = fields.Date("Date du Premier Paiement", compute='_compute_reminder_dates')
    second_payment_date = fields.Date("Date du Deuxième Paiement", compute='_compute_reminder_dates')
    third_payment_date = fields.Date("Date du Troisième Paiement", compute='_compute_reminder_dates')

    amount_date1 = fields.Monetary("Versement 1", compute="_compute_amount_date")
    amount_date2 = fields.Monetary("Versement 2", compute="_compute_amount_date")
    amount_date3 = fields.Monetary("Versement 3", compute="_compute_amount_date")

    #_sql_constraints = [('days_uniq', 'unique(tracker_id, delay)', 'Days of the follow-up levels must be different')]
    _sql_constraints = [('days_uniq', 'unique(delay)', 'Days of the follow-up levels must be different')]

    @api.depends('manual_action_responsible_id')
    def _nb_relance(self):
        for tracked in self:
            if tracked.manual_action_responsible_id == tracked.user_id:
                tracked.is_responsible = True
            else:
                tracked.is_responsible = False


    @api.depends("sale_order_id.date_order")
    def _get_due_date(self):
        for tracked in self:
            date_order = tracked.sale_order_id.date_order
            duree = timedelta(days=60)
            # today = fields.Date.context_today(tracked)
            # due_date = today + relativedelta(months=3)
            if date_order:
                tracked.due_date = date_order + duree
            else:
                tracked.due_date = datetime.today()

    @api.depends("sale_order_id")
    def _get_amount_payment(self):
        for tracker in self:
            amount_payed = sum(tracker.sale_order_id.order_line.invoice_lines.move_id.filtered(
                lambda x: x.payment_state in ('paid', 'partial')).invoice_line_ids.mapped('price_subtotal'))
            tracker.amount_paid = amount_payed
            tracker.amount_remaining = tracker.amount_to_paid - tracker.amount_paid

    def _check_description(self):
        lang = self.env.user.lang
        for line in self:
            if line.description:
                try:
                    line.description % {'partner_name': '', 'date': '', 'user_signature': '', 'company_name': ''}
                except:
                    return False

        return True

    def send_email_relance(self):
        template_id = self.env.ref('orbit.email_template_account_tracker_client').id or self.email_template_id.id
        template = self.env['mail.template'].browse(template_id)
        if template:
            template.send_mail(self.id, force_send=True, email_values={
                'email_to': self.client.email,
            })

    def send_letter_relance(self):
        pass

    @api.depends('sale_order_id.date_order', 'sale_order_id.expiration_date')
    def _compute_reminder_dates(self):
        for tracker in self:
            if tracker.sale_order_id.date_order and tracker.sale_order_id.expiration_date:
                # period = order.expiration_date - order.date_order.date()
                # part = period / 3
                tracker.first_payment_date = tracker.sale_order_id.date_order
                tracker.second_payment_date = tracker.sale_order_id.expiration_date - timedelta(days=30)
                tracker.third_payment_date = tracker.sale_order_id.expiration_date  # Date de Livraison
            else:
                tracker.first_payment_date = False
                tracker.second_payment_date = False
                tracker.third_payment_date = False

    @api.depends('sale_order_id.order_line.price_subtotal', 'sale_order_id.order_line.price_tax', 'sale_order_id.order_line.price_total')
    def _compute_amount_date(self):
        for so in self:
            order_lines = so.sale_order_id.order_line.filtered(lambda x: not x.display_type)
            amount_total = sum(order_lines.mapped('price_subtotal')) + sum(order_lines.mapped('price_tax'))
            so.amount_date1 = round(amount_total * 0.3, 2)
            so.amount_date2 = round(amount_total * 0.3, 2)
            so.amount_date3 = round(amount_total * 0.4, 2)

    # _constraints = [
    #     (_check_description,
    #      'Your description is invalid, use the right legend or %% if you want to use the percent character.',
    #      ['description']),
    # ]