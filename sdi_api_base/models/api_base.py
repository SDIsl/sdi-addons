###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import _, api, models
from odoo.exceptions import UserError
from typing import Union
from urllib import parse
import requests


SUPPORTED_METHODS = ['GET', 'POST', 'PUT']


class APIBase(models.TransientModel):
    _name = 'api.base'
    _description = 'API Base'

    @api.model
    def get_connection(self):
        connection = self.search([], limit=1)
        if not connection:
            connection = self.sudo().create({})
        return connection

    @api.model
    def _status_control(self, response: requests.Response):
        if not int(response.status_code) < 400:
            url = parse.unquote_plus(response.url)
            content = str(response.content, 'utf8')
            raise UserError(
                f'Error {response.status_code} ' +
                _('in API call') +
                f':\n{url}: \n\n{content}'
            )

    @api.model
    def _prepare_request(
        self,
        params: Union[dict, str] = None,
        headers: dict = None
    ) -> tuple:
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        if isinstance(params, dict):
            params = parse.urlencode(params)
        return (params, headers)

    @api.model
    def _request(
        self,
        method: str,
        url: str = '',
        data=None,
        params: Union[dict, str] = None,
        headers: dict = None
    ) -> requests.Response:
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        (params, headers) = self._prepare_request(
            params=params,
            headers=headers
        )

        if method not in SUPPORTED_METHODS:
            raise UserError(_('Unsupported method') + f' "{method}" ' +
                            _('in API call') + '.')
        response = None
        if method == 'GET':
            response = requests.get(
                url,
                params=params,
                headers=headers,
            )
        if method == 'POST':
            response = requests.post(
                url,
                json=data,
                params=params,
                headers=headers,
            )
        if method == 'PUT':
            response = requests.put(
                url,
                json=data,
                params=params,
                headers=headers,
            )
        self._status_control(response)
        return response

    @api.model
    def get(
        self,
        url: str = '',
        params: Union[dict, str] = None,
        headers: dict = None
    ) -> requests.Response:
        return self._request(
            method='GET',
            url=url,
            params=params,
            headers=headers,
        )

    @api.model
    def post(
        self,
        url: str = '',
        data=None,
        params: Union[dict, str] = None,
        headers: dict = None
    ) -> requests.Response:
        return self._request(
            method='POST',
            data=data,
            url=url,
            params=params,
            headers=headers,
        )

    @api.model
    def put(
        self,
        url: str = '',
        data=None,
        params: Union[dict, str] = None,
        headers: dict = None
    ) -> requests.Response:
        return self._request(
            method='PUT',
            data=data,
            url=url,
            params=params,
            headers=headers,
        )
