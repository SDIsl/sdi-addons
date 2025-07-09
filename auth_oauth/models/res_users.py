# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
from wsgiref import headers
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons import base
base.models.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    oauth_provider_id = fields.Many2one('auth.oauth.provider', string='OAuth Provider')
    oauth_uid = fields.Char(string='OAuth User ID', help="Oauth Provider user_id", copy=False)
    oauth_access_token = fields.Char(string='OAuth Access Token', readonly=True, copy=False)

    _sql_constraints = [
        ('uniq_users_oauth_provider_oauth_uid', 'unique(oauth_provider_id, oauth_uid)', 'OAuth UID must be unique per provider'),
    ]

    @api.model
    def _auth_oauth_rpc(self, endpoint, access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
        }
        return requests.get(endpoint, headers=headers).json()

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token)
            validation.update(data)
        return validation

    @api.model
    def _generate_signup_values(self, provider, validation, params):
        oauth_uid = validation['user_id']
        email = validation.get('email', 'provider_%s_user_%s' % (provider, oauth_uid))
        name = validation.get('name', email)
        return {
            'name': name,
            'login': email,
            'email': email,
            'oauth_provider_id': provider,
            'oauth_uid': oauth_uid,
            'oauth_access_token': params['access_token'],
            'active': True,
        }

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        # Omito comportamiento por defecto. Tiraba del user_id del que no dispongo en esta configuración Azure para Heráclito
        """ retrieve and sign in the user corresponding to provider and validated access token
            :param provider: oauth provider id (int)
            :param validation: result of validation of access token (dict)
            :param params: oauth parameters (dict)
            :return: user login (str)
            :raise: AccessDenied if signin failed

            This method can be overridden to add alternative signin methods.
        """
        email = validation.get('email', 'not_found')
        try:
            oauth_user = self.search([("login", "=", email), ('oauth_provider_id', '=', provider)])
            if not oauth_user:
                oauth_user = self.search([("login", "=", email)])
            if not oauth_user:
                raise AccessDenied('No user found for this OAuth provider and email {}.'.format(email))
            if len(oauth_user) != 1:
                _logger.warning('Multiple users found for OAuth provider %s and email %s. Using the first one.', provider, email)
                oauth_user = oauth_user[0]
            oauth_user.write({'oauth_access_token': params['access_token'], 'oauth_provider_id': provider})
            return oauth_user.login
        except AccessDenied as access_denied_exception:
            if self.env.context.get('no_user_creation'):
                return None
            state = json.loads(params['state'])
            token = state.get('t')
            values = self._generate_signup_values(provider, validation, params)
            try:
                _, login, _ = self.signup(values, token)
                return login
            except (SignupError, UserError):
                raise access_denied_exception

    @api.model
    def auth_oauth(self, provider, params):
        # Advice by Google (to avoid Confused Deputy Problem)
        # if validation.audience != OUR_CLIENT_ID:
        #   abort()
        # else:
        #   continue with the process
        access_token = params.get('access_token')
        validation = self._auth_oauth_validate(provider, access_token)
        # required check
        if not validation.get('email'):
            # Workaround: facebook does not send 'user_id' in Open Graph Api
            if validation.get('id'):
                validation['user_id'] = validation['id']
            else:
                raise AccessDenied()

        # retrieve and sign in user
        login = self._auth_oauth_signin(provider, validation, params)
        if not login:
            raise AccessDenied()
        # return user credentials
        return (self.env.cr.dbname, login, access_token)

    def _check_credentials(self, password):
        try:
            return super(ResUsers, self)._check_credentials(password)
        except AccessDenied:
            res = self.sudo().search([('id', '=', self.env.uid), ('oauth_access_token', '=', password)])
            if not res:
                raise

    def _get_session_token_fields(self):
        return super(ResUsers, self)._get_session_token_fields() | {'oauth_access_token'}
