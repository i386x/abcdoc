#
# File:    ./tests/unit/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-04-25 03:06:11 +0200
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Unit tests utilities.

.. include:: defs.inc
"""

from sphinx_abcdoc_theme.utils import FileAsset


class NoFileAsset:
    """A class that do not implement |FileAsset|."""

    __slots__ = ()


class FileAssetImpl(FileAsset):
    """|FileAsset| implementation."""

    __slots__ = ()

    @property
    def filename(self):
        """
        Return the file path.

        :return: the file path

        Dummy implementation of the abstract property.
        """
        return super().filename


class FileAssetLike:
    """|FileAsset| interface implementation."""

    #: The dummy |FileAsset.filename| property
    filename = "foo"

    __slots__ = ()


class FakeNode:
    """Fake document node."""

    #: The tag name
    tagname = "fake"
    #: Fake node attributes
    attributes = {"source": "index.rst"}
    #: The fake current line location of the fake node
    current_line = 42

    __slots__ = ()


class NodeWithoutTagname:
    """Fake document node without the ``tagname`` attribute."""

    __slots__ = ()


class NodeWithNoneTagname:
    """Fake document node with the :obj:`None` ``tagname`` attribute."""

    #: The tag name
    tagname = None

    __slots__ = ()


class NodeWithTagname:
    """Fake document node with the ``tagname`` attribute set."""

    #: The tag name
    tagname = "tag"

    __slots__ = ()
