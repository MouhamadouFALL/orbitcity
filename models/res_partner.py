# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_enterprise = fields.Boolean(string="Est Entreprise", default=False)
    is_main_contact = fields.Boolean(string="Contact Principal", default=False)
    register_com = fields.Char('Registre Commercial')
    ninea = fields.Char(string='NINEA')

    role = fields.Selection([
            ('main_user', 'Utilisateur Principal'),
            ('secondary_user', 'Utilisateur Secondaire')
        ], string='Rôle', default='secondary_user')
    adhesion = fields.Selection([
            ('pending', 'En cours de validation'),
            ('accepted', 'Accepté'),
            ('rejected', 'Rejeté')
        ], string='Adhésion', default='pending')
    
    # Nouveau champ pour le responsable du suivi
    payment_responsible_id = fields.Many2one('res.users', string='Follow-up Responsible',
                                             help="Optionally you can assign a user to this field, which will make him responsible for the action.",
                                             copy=False, ondelete='set null', )

    # Nouveau champ pour la promesse de paiement du client
    payment_note = fields.Text('Customer Payment Promise', help="Payment Note", copy=False)

    # Nouveau champ pour la prochaine action
    payment_next_action = fields.Text('Next Action', copy=False,
                                      help="This is the next action to be taken. It will automatically be set when the partner gets a follow-up level that requires a manual action.",
                                      )

    # Nouveau champ pour la date de la prochaine action
    payment_next_action_date = fields.Date('Next Action Date', copy=False,
                                           help="This is when the manual follow-up is needed. "
                                                "The date will be set to the current date when the partner "
                                                "gets a follow-up level that requires a manual action. "
                                                "Can be practical to set manually e.g. to see if he keeps "
                                                "his promises.")

    # Nouveau champ pour les écritures comptables non réconciliées
    unreconciled_aml_ids = fields.One2many('account.move.line', 'partner_id',
                                           domain=[('reconciled', '=', False), ('move_id.state', '!=', 'draft')])

    # Nouveau champ pour la dernière date de suivi
    latest_followup_date = fields.Date('Latest Follow-up Date', compute='_compute_latest', store=False,
                                       help="Latest date that the follow-up level of the partner was changed")
    

