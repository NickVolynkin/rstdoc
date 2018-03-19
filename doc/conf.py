extensions = ['sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    ]
numfig = False
templates_path = ['_templates']
source_suffix = '.rest'
master_doc = 'index'
project = 'sample'
author = project+' Project Team'
copyright = '2017, '+author
version = '1.0'
release = '1.0.0'
language = None
exclude_patterns = []
pygments_style = 'sphinx'
todo_include_todos = True
import sphinx_bootstrap_theme
html_theme = 'bootstrap'
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
latex_engine = 'xelatex'
tikz_transparent = True
tikz_proc_suite = 'ImageMagick'
tikz_tikzlibraries = 'arrows,snakes,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks,intersections'
tikz_latex_preamble = r"""
\usepackage{unicode-math}
\usepackage{tikz}
%\usepackage{tikz-uml}
\usepackage{caption}
\captionsetup[figure]{labelformat=empty}
"""
latex_elements = {
'preamble':tikz_latex_preamble+r"\usetikzlibrary{""" + tikz_tikzlibraries+ '}'
}
latex_documents = [
    (master_doc, project.replace(' ','')+'.tex',project+' Documentation',author,'manual'),
]