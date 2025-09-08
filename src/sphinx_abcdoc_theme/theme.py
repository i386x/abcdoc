#
# File:    ./src/sphinx_abcdoc_theme/theme.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-12-15 19:26:09 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Theme entry point.

.. include:: defs.inc
"""

import pathlib
import re
from typing import TYPE_CHECKING

from sphinx.errors import ThemeError

from sphinx_abcdoc_theme.utils import (
    CAPTION_ATTR,
    CLASSES_ATTR,
    NAMES_ATTR,
    NAVBAR_ATTR,
    FileAsset,
)
from sphinx_abcdoc_theme.writer import HtmlTranslator

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence
    from typing import ClassVar

    from sphinx_abcdoc_theme import BuildEnvironment
    from sphinx_abcdoc_theme import Compound as compound
    from sphinx_abcdoc_theme import Document as document
    from sphinx_abcdoc_theme import Element, PageContext
    from sphinx_abcdoc_theme import Section as section
    from sphinx_abcdoc_theme import (
        Sphinx,
        SphinxTransform,
        StandaloneHTMLBuilder,
        StrPath,
        global_toctree_for_doc,
        make_id,
    )
else:
    from docutils.nodes import Element, compound, section
    from sphinx.builders.html import StandaloneHTMLBuilder
    from sphinx.environment.adapters.toctree import global_toctree_for_doc
    from sphinx.transforms import SphinxTransform
    from sphinx.util.nodes import make_id

#: The ``fragment`` key name
FRAGMENT_KEY: str = "fragment"
#: The ``toctree-wrapper`` class name
TOCTREE_WRAPPER_CLASS: str = "toctree-wrapper"


class PutTocInsideSection(SphinxTransform):
    """
    Put the *Table of Contents* inside a |section| node.

    The *Table of Contents* is wrapped inside the |compound| document node with
    ``classes`` attribute containing ``toctree-wrapper``. The first child of
    this |compound| node is a |toctree| node containing table of contents
    document tree and related attributes, like ``caption``.

    By applying this transform, a new id is made first, either from the
    ``caption`` attribute if it is given or from a random generated value. This
    id is then added to the newly created |section| document node, which
    becomes a replacement for the |compound| node in the document tree,
    inheriting all its children.
    """

    #: The |default priority| of this transform
    default_priority: "ClassVar[int | None]" = 702

    __slots__ = ()

    def apply(self, **unused_kwargs: object) -> None:
        """
        Apply the transform.

        :param unused_kwargs: Key-value arguments
        """
        env: "BuildEnvironment" = self.document.settings.env
        for node in self.document.findall(compound):
            if TOCTREE_WRAPPER_CLASS not in node.get(CLASSES_ATTR, []):
                continue
            term: "str | None" = (
                node[0].get(CAPTION_ATTR)
                if len(node) > 0 and isinstance(node[0], Element)
                else None
            )
            name: str = make_id(env, self.document, term=term)
            new_node: section = section()
            new_node[NAMES_ATTR].append(name)
            new_node.extend(node)
            self.document.note_implicit_target(new_node, new_node)
            node.replace_self(new_node)


def setup_context(
    app: "Sphinx",
    pagename: str,
    unused_templatename: str,
    context: "PageContext",
    unused_doctree: "document",
) -> None:
    """
    Customize the page context.

    :param app: The Sphinx application instance
    :param pagename: The page name
    :param unused_templatename: The template name
    :param context: The context for the template engine
    :param unused_doctree: The document tree

    Customize the page context used by the template engine during the page
    rendering:

    * ``author``, ``description``, and ``keywords`` are passed from the Sphinx
      configuration
    * ``navbar()`` function is added
    * ``fsfilter(files, regex)`` function is added
    """

    def navbar() -> str:
        """
        Render the navigation bar.

        :return: the navigation bar rendered as HTML
        :raises ThemeError: when there are no |toctree| nodes or the builder is
            not :class:`~sphinx.builders.html.StandaloneHTMLBuilder`

        Tag |toctree| node with ``navbar`` attribute so the |HTML translator|
        can distinguish the navigation bar document tree from the main document
        tree.
        """
        toctree: "Element | None" = global_toctree_for_doc(
            app.builder.env,
            pagename,
            app.builder,
            collapse=True,
            includehidden=True,
            maxdepth=1,
        )
        if toctree is None:
            raise ThemeError("Document has no toctree nodes")
        toctree[NAVBAR_ATTR] = True
        if not isinstance(app.builder, StandaloneHTMLBuilder):
            raise ThemeError(
                "`navbar()` can be only used within the `html` output context"
            )
        return app.builder.render_partial(toctree)[FRAGMENT_KEY]

    def fsfilter(
        files: "Sequence[FileAsset | StrPath]", regex: str
    ) -> "Iterator[FileAsset | StrPath]":
        """
        Filter file system objects.

        :param files: The list of file system objects
        :param regex: The regular expression used to filter :xarg:`files` by
            their base names
        :return: the sequence of file system objects matching :xarg:`regex`

        Iterate through :xarg:`files` and return those with the base name that
        matches :xarg:`regex`.
        """
        reobj: "re.Pattern[str]" = re.compile(regex)
        for item in files:
            basename: str = (
                pathlib.Path(
                    item.filename if isinstance(item, FileAsset) else item
                )
                .resolve()
                .name
            )
            if reobj.match(basename):
                yield item

    context["author"] = app.config.author
    context["description"] = app.config.description
    context["keywords"] = app.config.keywords
    context["navbar"] = navbar
    context["fsfilter"] = fsfilter


def setup(app: "Sphinx") -> None:
    """
    Set up |abcdoc| theme.

    :param app: The Sphinx application instance
    """
    app.add_config_value("abcdoc_debug", False, "env")
    app.add_config_value("description", "", "env")
    app.add_config_value("keywords", [], "env")
    app.add_transform(PutTocInsideSection)
    app.add_html_theme("abcdoc", pathlib.Path(__file__).resolve().parent)
    app.set_translator("html", HtmlTranslator, override=True)
    app.connect("html-page-context", setup_context)
