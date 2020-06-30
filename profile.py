import os

from recon.core.module import BaseModule
from recon.mixins.resolver import ResolverMixin
from recon.mixins.threads import ThreadingMixin


class Module(BaseModule, ResolverMixin, ThreadingMixin):

    # modules are defined and configured by the "meta" class variable
    # "meta" is a dictionary that contains information about the module, ranging from basic information, to input that affects how the module functions
    # below is an example "meta" declaration that contains all of the possible definitions

    meta = {
        'name': 'Companies House',
        'author': 'drag0ns3c (@drag0ns3c)',
        'version': '1.0',
        'description': 'Searches the Companies House register (UK)',
        'dependencies': [],
        'files': [],
        'required_keys': ['ch_api'],
        'comments': '',
        'query': 'SELECT DISTINCT host FROM hosts WHERE host IS NOT NULL',
        'options': (
            ('company_number', '8.8.8.8', 'no', 'the company number'),
        ),
    }

    # mandatory method
    # the second parameter is required to capture the result of the "SOURCE" option, which means that it is only required if "query" is defined within "meta"
    # the third parameter is required if a value is returned from the "module_pre" method
    def module_run(self, hosts):
        self.output(self.options)
        self.output('Companies House search...')
        # self.thread(hosts, url, headers)
