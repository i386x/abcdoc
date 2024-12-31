#
# File:    ./docs/conf.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2019-02-16 18:22:38 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""Configuration for Sphinx documentation builder."""

from sphinx_abcdoc_theme.version import __version__


project = "abcdoc"
description = "Tools for generating a documentation"
author = "Jiří Kučera"
copyright = "2018-%Y, Jiří Kučera"
version = ".".join(__version__.split(".")[:2])
release = __version__

needs_sphinx = "8.1"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx_abcdoc_theme",
]
manpages_url = (
    "https://man7.org/linux/man-pages/"
    "man{section}/{page}.{section}.html"
)
today_fmt = "%Y-%m-%d"

numfig = True
numfig_format = {
    "code-block": "Listing %s",
    "figure": "Figure %s",
    "section": "Section",
    "table": "Table %s",
}
numfig_secnum_depth = 0

highlight_language = "python"

language = "en"

option_emphasize_placeholders = True
primary_domain = "py"

nitpicky = True

maximum_signature_line_length = 79
strip_signature_backslash = True

exclude_patterns = ["build"]

smartquotes_action = "qBDew"

html_theme = "abcdoc"
html_title = f"{project} {release} Documentation"
html_short_title = f"{project} {release} documentation"
html_last_updated_fmt = "%Y-%m-%d %H:%M:%S %z"
html_permalinks_icon = "&#x00B6;"
html_secnumber_suffix = " "

text_secnumber_suffix = " "

man_pages = [
    (root_doc, project, description, author, "7"),
]

linkcheck_report_timeouts_as_broken = True

c_maximum_signature_line_length = maximum_signature_line_length

cpp_maximum_signature_line_length = maximum_signature_line_length

javascript_maximum_signature_line_length = maximum_signature_line_length

python_display_short_literal_types = True
python_maximum_signature_line_length = maximum_signature_line_length

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}
