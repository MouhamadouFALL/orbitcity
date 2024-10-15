#-*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    attachment_ids = fields.Many2many('ir.attachment', 'orbit_attachment_rel', 'orbit_id', 'attachment_id', string="Pieces jointes", store=True, help="Attach files related to this order")

    usr_confirmed = fields.Many2one('res.users', string="Confirmé par", readonly=True)

    def button_confirm(self):
        """Overrides the confirm button method to record the user who confirmed."""
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            # Enregistre l'utilisateur connecté
            order.usr_confirmed = self.env.user  
        return res