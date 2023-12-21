project = 'Berrymill'
copyright = '2023, Bo Maryniuk'
author = 'Bo Maryniuk'
release = 'pre-release'
version = "0.1"

extensions = [
    "sphinx_rtd_theme",
]

templates_path = ['_templates']
exclude_patterns = ['_build']

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
}

html_show_sourcelink = False
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
