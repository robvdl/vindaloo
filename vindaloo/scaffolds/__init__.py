from pyramid.scaffolds import PyramidTemplate

from vindaloo.version import VERSION
from vindaloo.security import generate_secret_key


class VindalooTemplate(PyramidTemplate):
    _template_dir = 'vindaloo'
    summary = 'vindaloo API project'

    def pre(self, command, output_dir, vars):
        vars['project_version'] = '0.0.1'
        vars['vindaloo_version'] = VERSION
        vars['secret_key'] = generate_secret_key(40)
        return super().pre(command, output_dir, vars)
