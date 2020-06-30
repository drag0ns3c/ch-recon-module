import requests
from requests.auth import HTTPBasicAuth

from recon.core.module import BaseModule
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin

BASE_URL = 'https://api.companieshouse.gov.uk'


class Module(BaseModule, ResolverMixin, ThreadingMixin):
    meta = {
        'name': 'Companies House',
        'author': 'drag0ns3c (@drag0ns3c)',
        'version': '1.0',
        'description': 'Searches the Companies House register (UK)',
        'dependencies': [],
        'files': [],
        'required_keys': ['ch_api'],
        'options': (
            ('company_number', '00399642', 'no', 'the company number'),
        ),
    }

    def _ch_api_get(self, company_number, path=''):
        api_key = self.keys.get('ch_api')
        if not api_key:
            self.error(('You need to set the ch_api key. Head over to '
                        'https://developer.companieshouse.gov.uk to create one'))
            return

        auth = HTTPBasicAuth(api_key, '')
        url = BASE_URL + f'/company/{company_number}' + path
        response = requests.get(url, auth=auth)

        self.output(url)
        if not response.ok:
            if response.status_code == 404:
                self.error(f'No company found with number {company_number}')
            else:
                self.error(('failed to get an okay response. status: '
                            f'{response.status_code}.'))
            return

        return response.json()

    def module_run(self):
        company_number = self.options.get('COMPANY_NUMBER')
        company_number = f'{company_number:08d}'
        profile = self._ch_api_get(company_number)
        notes = [
            f'Company number {company_number}',
            f'Type: {profile.get("type", "unknown")}',
            f'Status: {profile.get("company_status", "unknown")}',
            f'Link: https://beta.companieshouse.gov.uk/company/{company_number}',
        ]
        self.insert_companies(
            company=profile['company_name'],
            notes=', '.join(notes),
        )

        # registered office address for the company
        roa = self._ch_api_get(company_number, '/registered-office-address')
        if roa:
            street_address = [
                roa.get('address_line_1', ''),
                roa.get('address_line_2', ''),
                roa.get('country', ''),
                roa.get('locality', ''),
                roa.get('postal_code', ''),
                roa.get('region', ''),
            ]
            self.insert_locations(street_address=', '.join(street_address))

        # company officers
        officers = self._ch_api_get(company_number, '/officers')
        if officers:
            for officer in officers['items']:
                self.insert_contacts(
                    first_name=officer['name'],
                    country=officer.get('nationality'),
                    notes='officer',
                )

        # persons of significant control
        pscs = self._ch_api_get(
            company_number,
            '/persons-with-significant-control'
        )
        if pscs:
            for psc in pscs['items']:
                kwargs = {
                    'notes': 'psc',
                    'country': psc.get('nationality'),
                }
                if 'name_elements' in psc:
                    kwargs.update({
                        'first_name': psc['name_elements'].get('forename', ''),
                        'last_name': psc['name_elements'].get('surname', ''),
                        'title': psc['name_elements'].get('title'),
                    })
                else:
                    kwargs.update({'first_name': psc['name']})
                self.insert_contacts(**kwargs)
