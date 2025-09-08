#
# File:    ./tests/unit/test_theme.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-12-16 00:42:01 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Test :mod:`sphinx_abcdoc_theme.theme` module.

.. include:: defs.inc
"""

from sphinx.builders.html._assets import _CascadingStyleSheet, _JavaScript
from vutils.testing.testcase import TestCase

from .utils import make_application


class PageContextTestCase(TestCase):
    """
    Test case for page context.

    Some parts of page context are also tested in :mod:`.test_writer`.
    """

    __slots__ = ("app", "context")

    def setUp(self):
        """Set up the test."""
        #: The |Sphinx| application instance or mock
        self.app = make_application()
        #: The page context
        self.context = {}
        self.app.events.emit_firstresult(
            "html-page-context", "index", "page.html", self.context, None
        )

    def test_fsfilter(self):
        """Test ``fsfilter``."""
        assets = [
            "style_a.css",
            _CascadingStyleSheet("style_b.css"),
            "script_c.js",
            _JavaScript("script_d.js"),
            "wrong_a.css",
            _CascadingStyleSheet("wrong_b.css"),
            "wrong_c.js",
            _JavaScript("wrong_d.js"),
        ]
        self.assertEqual(
            list(self.context["fsfilter"](assets, r"(?!wrong_.\.(css|js))")),
            assets[:4],
        )
