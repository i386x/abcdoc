#
# File:    ./tests/unit/test_utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-04-25 02:11:44 +0200
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Test :mod:`sphinx_abcdoc_theme.utils` module.

.. include:: defs.inc
"""

import re

from docutils.nodes import Text
from sphinx.builders.html._assets import _CascadingStyleSheet, _JavaScript
from vutils.testing.mock import make_mock
from vutils.testing.testcase import TestCase
from vutils.testing.utils import make_type

from sphinx_abcdoc_theme.utils import (
    FileAsset,
    html_escape,
    indent_text,
    indentation,
    log_node_end,
    log_node_start,
    node_attribute_as_str,
    tagname,
    tokenize,
    wrap,
)


class FileAssetTestCase(TestCase):
    """Test case for |FileAsset|."""

    __slots__ = ()

    def test_file_asset(self):
        """Test |FileAsset|."""
        self.assertNotIsInstance(make_type("NoFileAsset")(), FileAsset)
        self.assertIsInstance(
            make_type("FileAssetLike", members={"filename": "foo"})(),
            FileAsset,
        )
        self.assertIsInstance(_CascadingStyleSheet("style.css"), FileAsset)
        self.assertIsInstance(_JavaScript("script.js"), FileAsset)


class HtmlEscapeTestCase(TestCase):
    """Test case for |html_escape|."""

    __slots__ = ()

    def test_html_escape(self):
        """Test |html_escape|."""
        self.assertEqual(
            html_escape('  \n\t"< >&|\n@#'), " &quot;&lt; &gt;&amp;| &#64;#"
        )


class IndentationTestCase(TestCase):
    """Test case for indentation functions."""

    __slots__ = ()

    def test_indentation(self):
        """Test |indentation|."""
        self.assertEqual(indentation(0), "")
        self.assertEqual(indentation(1), " ")
        self.assertEqual(indentation(2), "  ")
        self.assertEqual(indentation(0, 2), "")
        self.assertEqual(indentation(1, 2), "  ")
        self.assertEqual(indentation(2, 2), "    ")
        self.assertEqual(indentation(0, 0), "")
        self.assertEqual(indentation(1, 0), "")
        self.assertEqual(indentation(2, 0), "")

    def test_indent_text(self):
        """Test |indent_text|."""
        self.assertEqual(indent_text("abc", 0), "abc")
        self.assertEqual(indent_text("abc", 1), " abc")
        self.assertEqual(indent_text("abc", 2), "  abc")
        self.assertEqual(indent_text("abc", 0, 4), "abc")
        self.assertEqual(indent_text("abc", 1, 4), "    abc")
        self.assertEqual(indent_text("abc", 2, 4), "        abc")
        self.assertEqual(indent_text("abc", 0, 0), "abc")
        self.assertEqual(indent_text("abc", 1, 0), "abc")
        self.assertEqual(indent_text("abc", 2, 0), "abc")


class TokenizeTestCase(TestCase):
    """Test case for |tokenize|."""

    __slots__ = ()

    def test_tokenize(self):
        """Test |tokenize|."""
        tokenizer = re.compile(r"[a-z]+|\s+")
        self.assertEqual(
            list(tokenize("abc   \t\t def   ", tokenizer)), ["abc", "def"]
        )

        result = []
        with self.assertRaisesRegex(ValueError, "at 18$"):
            for token in tokenize("   ab   cd \t ef \n @gh ij ", tokenizer):
                result.append(token)
        self.assertEqual(result, ["ab", "cd", "ef"])


class WrapTestCase(TestCase):
    """Test case for |wrap|."""

    __slots__ = ()

    def test_wrap(self):
        """Test |wrap|."""
        text = "abc  abc abc \t abcdefgh\n\n  "

        self.assertEqual(list(wrap("", 10)), [])
        self.assertEqual(list(wrap("", 10, 4)), [])
        self.assertEqual(list(wrap("  abcdefghij", 10)), ["abcdefghij\n"])
        self.assertEqual(list(wrap("abcdefghij", 10, 4)), ["    abcdefghij\n"])
        self.assertEqual(list(wrap(text, 10)), ["abc abc abc\n", "abcdefgh\n"])
        self.assertEqual(
            list(wrap(text, 10, 4)),
            ["    abc abc\n", "    abc\n", "    abcdefgh\n"],
        )

        lines = []
        with self.assertRaises(ValueError):
            for line in wrap(
                "@@@ @@@ @@@ @@@ @@# @@@", 8, 2, re.compile(r"@+|\s+")
            ):
                lines.append(line)
        self.assertEqual(lines, ["  @@@ @@@\n", "  @@@ @@@\n"])


class NodeLoggingTestCase(TestCase):
    """Test case for |Node| logging functions."""

    __slots__ = (
        "fake_node",
        "node_without_tagname",
        "node_with_none_tagname",
        "node_with_tagname",
    )

    def setUp(self):
        """Set up the test."""
        #: The fake document node
        self.fake_node = make_type(
            "FakeNode",
            members={
                "tagname": "fake",
                "attributes": {"source": "index.rst"},
                "current_line": 42,
            },
        )()
        #: The fake document node without ``tagname``
        self.node_without_tagname = make_type("NodeWithoutTagname")()
        #: The fake document node with ``tagname`` set to :obj:`None`
        self.node_with_none_tagname = make_type(
            "NodeWithNoneTagname", members={"tagname": None}
        )()
        #: The fake document node with just ``tagname``
        self.node_with_tagname = make_type(
            "NodeWithTagname", members={"tagname": "tag"}
        )()

    def test_attribute_to_string(self):
        """Test an attribute to sting conversion."""
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "unknown", 1), ""
        )
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "unknown", 1, "(", ")"), ""
        )
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "current_line", 1),
            "  current_line: 42",
        )
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "current_line", 1, "(", ")"),
            "(  current_line: 42)",
        )
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "attributes", 1),
            "  source: index.rst",
        )
        self.assertEqual(
            node_attribute_as_str(self.fake_node, "attributes", 1, "(", ")"),
            "(  source: index.rst)",
        )

    def test_tagname(self):
        """Test the |tagname| helper."""
        self.assertEqual(
            tagname(self.node_without_tagname), "#node:NodeWithoutTagname"
        )
        self.assertEqual(
            tagname(self.node_with_none_tagname), "#node:NodeWithNoneTagname"
        )
        self.assertEqual(tagname(self.node_with_tagname), "tag")

    def test_node_logging(self):
        """Test |log_node_start| and |log_node_end|."""
        logger = make_mock(["debug"])

        log_node_start(self.node_with_tagname, 1, logger)
        self.assert_called_with(logger.debug, "%s", "  <tag>")

        log_node_start(self.fake_node, 1, logger)
        self.assert_called_with(
            logger.debug,
            "%s",
            "  <fake\n    source: index.rst\n    current_line: 42>",
        )

        log_node_start(Text("Hello!"), 1, logger)
        self.assert_called_with(logger.debug, "%s", "  <#text Hello!>")

        log_node_end(self.fake_node, 1, logger)
        self.assert_called_with(logger.debug, "%s</%s>", "  ", "fake")
