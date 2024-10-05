#-*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    attachment_ids = fields.Many2many('ir.attachment', 'orbit_attachment_rel', 'orbit_id', 'attachment_id', string="Pieces jointes", store=True, help="Attach files related to this order")


