# -*- coding: utf-8 -*-

import sys, os

project = u'cronwatch'
copyright = u'2011, David Lowry'
version = '1.4'
release = version

extensions = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = []

pygments_style = 'sphinx'

html_theme = 'default'
html_static_path = ['_static']
htmlhelp_basename = 'cronwatchdoc'

latex_documents = [
  ('index', 'cronwatch.tex', u'cronwatch Documentation',
   u'David Lowry', 'manual'),
]

man_pages = [
    ('index', 'cronwatch', u'cronwatch Documentation',
     [u'David Lowry'], 1)
]
