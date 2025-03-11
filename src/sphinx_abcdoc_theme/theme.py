#
# File:    ./src/sphinx_abcdoc_theme/theme.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-12-15 19:26:09 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""Theme entry point."""

import pathlib
import re

from docutils.nodes import compound, section

from sphinx.environment.adapters.toctree import global_toctree_for_doc
from sphinx.transforms import SphinxTransform
from sphinx.util.nodes import make_id

from sphinx_abcdoc_theme.writer import HtmlTranslator


class PutToCInsideSection(SphinxTransform):
    """"""

    default_priority = 702

    def apply(self):
        """"""
        env = self.document.settings.env
        for node in self.document.findall(compound):
            if "toctree-wrapper" not in node.get("classes", []):
                continue
            name = make_id(env, self.document, term=node[0].get("caption"))
            new_node = section()
            new_node["names"].append(name)
            new_node.extend(node)
            self.document.note_implicit_target(new_node, new_node)
            node.replace_self(new_node)


def setup_context(app, pagename, templatename, context, doctree):
    """"""

    def navbar():
        """"""
        toctree = global_toctree_for_doc(
            app.builder.env,
            pagename,
            app.builder,
            collapse=True,
            includehidden=True,
            maxdepth=1,
        )
        toctree["navbar"] = True
        return app.builder.render_partial(toctree)["fragment"]

    def fsfilter(files, regex):
        """"""
        reobj = re.compile(regex)
        for item in files:
            basename = pathlib.Path(
                item.filename if hasattr(item, "filename") else item
            ).resolve().name
            if reobj.match(basename):
                yield item

    context["author"] = app.config.author
    context["description"] = app.config.description
    context["keywords"] = app.config.keywords
    context["navbar"] = navbar
    context["fsfilter"] = fsfilter


def setup(app):
    """Setup |abcdoc| theme."""
    app.add_config_value("abcdoc_debug", False, "env")
    app.add_config_value("description", "", "env")
    app.add_config_value("keywords", [], "env")
    app.add_transform(PutToCInsideSection)
    app.add_html_theme("abcdoc", pathlib.Path(__file__).resolve().parent)
    app.set_translator("html", HtmlTranslator, override=True)
    app.connect("html-page-context", setup_context)
