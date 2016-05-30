from pyramid.scaffolds import PyramidTemplate

from vindaloo.version import VERSION


class VindalooTemplate(PyramidTemplate):
    _template_dir = 'vindaloo'
    summary = 'Vindaloo + SQLAlchemy API project'

    def pre(self, command, output_dir, vars):
        vars['project_version'] = '0.0.1'
        vars['vindaloo_version'] = VERSION
        return super().pre(command, output_dir, vars)
