# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Lead(models.Model):
    _inherit = "crm.lead"


    location = fields.Char('Localisation', store=True)

    def action_sale_quotations_new(self):
        if not self.partner_id:
            return self.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            return self.env["ir.actions.actions"]._for_xml_id("orbit.crm_type_sale_action")




