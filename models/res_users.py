# -*- coding: utf-8 -*-
from odoo import  fields, models, api, _, exceptions
import logging

_logger = logging.getLogger(__name__)

class Users(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):

        self.clear_caches()
        usrs = super(Users, self).create(vals_list)

        # Recupérer les groupe : "Groupe portal", "Internal User" et "Groupe public"
        portal_group = self.env.ref('base.group_portal')  # Identifier le groupe "Portal"
        internal_group = self.env.ref('base.group_user')  # Groupe "Internal User"
        public_group = self.env.ref('base.group_public')  # Groupe "Public"
        # _logger.info(f" portal_group: {portal_group}, internal_group: {internal_group}, public_group: {public_group} .")
        for usr in usrs:
            # Retirer l'utilisateur des autres types d'utilisateurs
            usr.groups_id = [(3, internal_group.id), (3, portal_group.id), (4, public_group.id)]

        return usrs
    
    def write(self, vals_list):
        """
        Else the menu will be still hidden even after removing from the list
        """
        usrs = super(Users, self).write(vals_list)
        for rec in self:
            for menu in rec.hide_menu_ids:
                menu.write({
                    'restrict_user_ids': [(4, rec.id)]
                })
        self.clear_caches()
        return usrs
    
    def _get_is_admin(self):
        """
        The Hide specific menu tab will be hidden for the Admin user form.
        Else once the menu is hidden, it will be difficult to re-enable it.
        """
        for usr in self:
            usr.is_admin = False
            if usr.id == self.env.ref('base.user_admin').id:
                usr.is_admin = True


    
    # main_company, user_root, user_admin, partner_admin

    hide_menu_ids = fields.Many2many('ir.ui.menu', string="Menus", store=True, 
                                     help="Select menu items that needs to be hidden to this user ")
    is_admin = fields.Boolean(string="Est Admin", compute=_get_is_admin)
    # for users web
    # is_web= fields.Boolean(string="User web ", default=True)
