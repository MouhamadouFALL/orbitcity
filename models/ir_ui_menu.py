# -*- coding: utf-8 -*-
from odoo import fields, models, api, _, exceptions


class RestrictMenu(models.Model):
    _inherit = 'ir.ui.menu'

    # edit_menu_access : vue menu
    restrict_user_ids = fields.Many2many('res.users')