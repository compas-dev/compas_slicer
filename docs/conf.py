# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sphinx_compas_theme

from sphinx.ext.napoleon.docstring import NumpyDocstring

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'COMPAS SLICER'
year = '2020'
author = 'Digital Building Technologies, Gramazio Kohler Research'
copyright = '{0}, {1}'.format(year, author)
version = release = '0.1.0'

pygments_style = 'sphinx'
show_authors = True
add_module_names = True
templates_path = ['_templates', ]
extlinks = {
    'issue': ('https://https://github.com/dbt-ethz/compas_slicer/issues/%s', '#'),
    'pr': ('https://https://github.com/dbt-ethz/compas_slicer/pull/%s', 'PR #'),
}

# intersphinx options
intersphinx_mapping = {'python': ('https://docs.python.org/', None),
                       'compas': ('http://compas-dev.github.io/main/', None)}

# autodoc options
autodoc_default_options = {
    'member-order': 'bysource',
    'exclude-members': '__weakref__',
    'undoc-members': True,
    'private-members': True,
    'show-inheritance': True,
}

autodoc_member_order = 'alphabetical'

# autosummary options
autosummary_generate = True

# # on_rtd is whether we are on readthedocs.org
# on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
html_theme = 'compaspkg'
html_theme_path = sphinx_compas_theme.get_html_theme_path()
html_theme_options = {
    "package_name": 'compas_slicer',
    "package_title": project,
    "package_version": release,
    "package_repo": 'https://https://github.com/dbt-ethz/compas_slicer',
}

html_split_index = False
html_short_title = '%s-%s' % (project, version)
html_context = {}
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
html_copy_source = False
html_show_sourcelink = False
html_add_permalinks = ''
html_experimental_html5_writer = True
html_compact_lists = True
html_extra_path = [".nojekyll"]

# napoleon options
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = False
napoleon_use_rtype = False

# Parse Attributes and Class Attributes on Class docs same as parameters.
# first, we define new methods for any new sections and add them to the class


def parse_keys_section(self, section):
    return self._format_fields('Keys', self._consume_fields())


NumpyDocstring._parse_keys_section = parse_keys_section


def parse_attributes_section(self, section):
    return self._format_fields('Attributes', self._consume_fields())


NumpyDocstring._parse_attributes_section = parse_attributes_section


def parse_class_attributes_section(self, section):
    return self._format_fields('Class Attributes', self._consume_fields())


NumpyDocstring._parse_class_attributes_section = parse_class_attributes_section


# we now patch the parse method to guarantee that the the above methods are
# assigned to the _section dict
def patched_parse(self):
    self._sections['keys'] = self._parse_keys_section
    self._sections['class attributes'] = self._parse_class_attributes_section
    self._unpatched_parse()


NumpyDocstring._unpatched_parse = NumpyDocstring._parse
NumpyDocstring._parse = patched_parse