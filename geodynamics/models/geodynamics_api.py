
import requests
from base64 import b64encode

from odoo import models, _

GEODYNAMICS_API_URI = "https://api.intellitracer.be/api/"

class GeodynamicsApi(models.AbstractModel):
    _name = 'geodynamics.api'
    _description = 'Geodynamics API wrapper'

    def _get_basic_auth_header(self):
        Parameters = self.env['ir.config_parameter'].sudo()
        
        company_name = Parameters.get_param('geodynamics.geo_company_name')
        user_name = Parameters.get_param('geodynamics.user_name')
        password = Parameters.get_param('geodynamics.password')

        return b64encode(f"{user_name}|{company_name}:{password}".encode(encoding='utf8')).decode(encoding='utf8')


    def load_postcalculation(self, date):
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Authorization'] = 'Basic %s' % self._get_basic_auth_header()

        body = {}
        body['AllUsers'] = True
        body['Date'] = date.isoformat()
        body['IncludeTimesheetEvents'] = True

        try:
            resp = requests.post("%sv1/postcalculation/export" % GEODYNAMICS_API_URI, headers=headers, json=body)
            resp.raise_for_status()
            content = resp.json()
        except IOError:
            error_msg = _("Something went wrong while exporting the postcalculation from Geodynamics.")
            raise self.env['res.config.settings'].get_config_warning(error_msg)

        return content