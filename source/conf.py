# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
sys.path.insert(0, os.path.abspath('../')) 




project = 'Bunker Management System - NEXUS 2'
copyright = '2024, NEXUS 2'
author = 'NEXUS 2'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # Soporta Google y NumPy docstring styles
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']


latex_engine = 'xelatex'
latex_documents = [
    ('index', 'Bunker Management System - NEXUS 2.tex', 'Bunker Management System',
     'NEXUS 2', 'manual'),
]

latex_elements = {
    'preamble': r'''
        % Aumenta el límite de anidación
        \usepackage{enumitem}
        \setlistdepth{20}
        \renewcommand{\theenumi}{\roman{enumi}}
        \renewcommand{\theenumii}{\alph{enumii}}
        \renewcommand{\labelenumii}{(\theenumii)}
        \renewcommand{\theenumiii}{\arabic{enumiii}}
        \renewcommand{\labelenumiii}{\theenumiii.}
        \renewcommand{\theenumiv}{\Alph{enumiv}}
        \renewcommand{\labelenumiv}{(\theenumiv)}
        \renewcommand{\theenumv}{\Roman{enumv}}
        \renewcommand{\labelenumv}{\theenumv.}
        \renewcommand{\theenumvi}{\arabic{enumvi}}
        \renewcommand{\labelenumvi}{(\theenumvi)}
    ''',
}
