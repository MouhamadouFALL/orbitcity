# -*- coding: utf-8 -*-
from odoo import  fields, models, api, _, exceptions

class Users(models.Model):
    _inherit = 'res.users'

    # for users web
    # is_web_user = fields.Boolean(string="User web ", default=True)

    @api.model_create_multi
    def create(self, vals_list):
        users = super(Users, self).create(vals_list)
        portal_group = self.env.ref('base.group_portal')  # Identifier le groupe "Portal"
        internal_group = self.env.ref('base.group_user')  # Groupe "Internal User"
        public_group = self.env.ref('base.group_public')  # Groupe "Public"

        for user in users:

            # Retirer l'utilisateur des autres types d'utilisateurs
            user.groups_id = [(3, internal_group.id), (3, public_group.id)]
            user.groups_id = [(4, portal_group.id)]

        return users
