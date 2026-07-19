#
# File:    ./src/sphinx_abcdoc_theme/writer/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-09-14 22:41:08 +0200
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""Writer utilities."""

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sphinx_abcdoc_theme import Element, StrPath

def node_source(
    node: "Element", default: "StrPath | None" = None
) -> "StrPath | None":
    """
    Get the document node source.

    :param node: The document node
    :param default: The default document node source
    :return: the document node source

    Get the source of :xarg:`node` if there is some. Otherwise, use
    :xarg:`default`.
    """
    if SOURCE_ATTR not in node:
        return default
    return node[SOURCE_ATTR]
