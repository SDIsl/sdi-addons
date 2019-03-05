# SDI
# © 2018 David Juaneda <djuaneda@sdi.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json

import requests
import logging
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_geolocation = logging.getLogger(__name__ + '.geolocation')


def geo_find(addr, api_key=False):
    if not addr:
        return None
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    if api_key:
        url = "".join([url, "?key=", api_key])
    try:
        result = requests.get(url, params={'sensor': 'false', 'address': addr}).json()
    except Exception as e:
        raise UserError(_('Cannot contact geolocation servers. Please make sure that your Internet connection is up and running (%s).') % e)
    if result['status'] != 'OK':
        return None
    try:
        geo = result['results'][0]['geometry']['location']
        return float(geo['lat']), float(geo['lng'])
    except (KeyError, ValueError):
        return None


def geo_query_address(street=None, zip=None, city=None, state=None, country=None):
    if country and ',' in country and (country.endswith(' of') or country.endswith(' of the')):
        # put country qualifier in front, otherwise GMap gives wrong results,
        # e.g. 'Congo, Democratic Republic of the' => 'Democratic Republic of the Congo'
        country = '{1} {0}'.format(*country.split(',', 1))
    return tools.ustr(', '.join(
        field for field in [street, ("%s %s" % (zip or '', city or '')).strip(), state, country]
        if field
    ))


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def geo_localize(self, log=True):
        # We need country names in English below
        for partner in self.with_context(lang='en_US'):
            api_key = self.env['ir.config_parameter'].sudo().get_param('google_maps_view_api_key')
            result = geo_find(geo_query_address(street=partner.street,
                                                zip=partner.zip,
                                                city=partner.city,
                                                state=partner.state_id.name,
                                                country=partner.country_id.name),
                              api_key)
            if result is None:
                result = geo_find(geo_query_address(city=partner.city,
                                                    state=partner.state_id.name,
                                                    country=partner.country_id.name),
                                  api_key)

            if result:
                partner.write({
                    'partner_latitude': result[0],
                    'partner_longitude': result[1],
                    'date_localization': fields.Date.context_today(partner)
                })
            if log:
                _geolocation.info("[{}] {} : {}-{}".
                                  format(partner.date_localization,
                                         partner.name,
                                         partner.partner_latitude,
                                         partner.partner_longitude))
        return True


    @api.model
    def upgrade_set_geolocation(self, customers, log=True):
        _geolocation.info('Start geolocation. Customers = {}'.format(len(customers)))
        i = 0
        for customer in customers:
            result = customer.geo_localize(log)
            if result and customer.date_localization:
                i += 1
                if i%100 == 0 and log:
                    _geolocation.info(' >>>>>>> Number of geolocated customers = {}'.format(i))
        fails = len(customers) - i
        _geolocation.info(' Number of non-geolocated customers  = {}'.format(fails))
        _geolocation.info(' ***** TOTAL of geolocated customers = {} *****'.format(i))
