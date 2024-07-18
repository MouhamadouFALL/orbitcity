# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class RegularOrder(models.Model):
    _name = 'regular.order'
    _description = 'Regular Order'
    _inherit = 'sale.order'




