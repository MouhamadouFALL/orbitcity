from odoo import http
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo import http
from odoo.exceptions import ValidationError

class ClientApi(http.Controller):

    @http.route('/api/client/signup', auth='public', methods=['POST'], csrf=False)
    def signup(self, **kwargs):
        try:
            # Créer un nouveau partenaire pour le client
            partner_values = {
                'name': kwargs.get('name'),
                'email': kwargs.get('email'),
                'phone': kwargs.get('phone'),
            }
            partner_id = http.request.env['res.partner'].sudo().create(partner_values)

            # Créer un nouvel utilisateur pour le client
            user_values = {
                'name': kwargs.get('name'),
                'login': kwargs.get('email'),
                'email': kwargs.get('email'),
                'password': kwargs.get('password'),
                'partner_id': partner_id.id,
                'groups_id': [(6, 0, [http.request.env.ref('base.group_user').id])],
            }
            http.request.env['res.users'].sudo().create(user_values)

            # Renvoie un message de succès
            return {'success': True, 'message': 'Inscription réussie'}

        except ValidationError as e:
            # Renvoie un message d'erreur si la validation échoue
            return {'success': False, 'message': str(e)}


class ClientApi(http.Controller):

    @http.route('/api/client/login', auth='public', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        try:
            # Trouver l'utilisateur à partir de l'adresse e-mail
            user = http.request.env['res.users'].sudo().search([('login', '=', kwargs.get('email'))], limit=1)

            # Vérifier le mot de passe de l'utilisateur
            if not user.check_password(kwargs.get('password')):
                raise SignupError('Mot de passe incorrect')

            # Renvoie un message de succès et les informations de l'utilisateur
            return {
                'success': True,
                'message': 'Connexion réussie',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': user.partner_id.phone,
                },
            }

        except SignupError as e:
            # Renvoie un message d'erreur si la connexion échoue
            return {'success': False, 'message': str(e)}
