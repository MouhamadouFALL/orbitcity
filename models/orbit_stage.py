# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


AVAILABLE_PRIORITIES = [
    ('0', 'Bas'),
    ('1', 'Moyen'),
    ('2', 'Important'),
    ('3', 'Urgent'),
]


class Stage(models.Model):
    """ Modèle pour les étapes d'une vente. """

    _name = "orbit.stage"
    _description = "Ventes Stages"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    # Permet de plier ou replier une étape
    fold = fields.Boolean('Folded in sale process')
    # Les exigences pour chaque étape
    requirements = fields.Text('Exigences', required=True, help="les exigences internes pour cette étape")
    visible = fields.Boolean(string='Visible', default=True)

    type_sale = fields.Selection(
        selection=[
            ('regularorder', "Commande"),
            ('preorder', "Precommande"),
            ('creditorder', "Commande credit"),
            ('allorder', "Etapes expedition"),
        ],
        string="Type", required=True, copy=False, index=True, )

    group_usr_id = fields.Many2many('res.groups', string='Groupe validation', help='Groupe user pouvant spécifique intervenir dans cette étape ')
    # This field for interface only
    group_count = fields.Integer('Nombre de groupe ', compute='_compute_group_count')

    next_stage_id = fields.Many2one('orbit.stage', string='Next Stage')

    @api.depends('group_usr_id')
    def _compute_group_count(self):
        # cat_id = self.env.ref('orbit.orbit_groups').id
        # self.group_count = self.env['res.groups'].search_count([(cat_id, 'in', 'category_id')])
        self.group_count = len(self.group_usr_id)
