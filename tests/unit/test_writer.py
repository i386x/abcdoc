#
# File:    ./tests/unit/test_writer.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-04-25 02:14:57 +0200
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Test :mod:`sphinx_abcdoc_theme.writer` module.

.. include:: defs.inc
"""

import logging

from docutils.nodes import (
    Element,
    Text,
    bullet_list,
    list_item,
    paragraph,
    reference,
    section,
    target,
    title,
)
from docutils.utils import new_document
from sphinx.addnodes import compact_paragraph
from sphinx.errors import ThemeError
from sphinx.transforms import SphinxTransform
from vutils.testing.testcase import TestCase
from vutils.yaml.load import load_yaml

from sphinx_abcdoc_theme.utils import (
    IDS_ATTR,
    LAST_CHAR_ATTR,
    NODE_ATTRIBUTES,
    node_attribute_as_str,
)
from sphinx_abcdoc_theme.writer import (
    NAVBAR_SCOPE,
    PARTIAL_NODE_NAME,
    AmbiguousIdsError,
    BrokenBodyError,
    ConflictingIdError,
    Context,
    ContextError,
    HtmlTranslator,
    HtmlTranslatorBase,
    MissingIdsError,
    MissingRefError,
    UnprocessedPendingIdsError,
    check_ids,
    get_id,
    ids2str,
    is_index,
    is_partial_node,
    node_source,
    tag_attr,
)

from .utils import (
    ModulePatcher,
    doctree2html,
    make_application,
    make_config,
    rst2html,
)


def document_with_conflicting_ids():
    """
    Create a document with conflicting ids.

    :return: the document (document tree) with conflicting ids
    """
    root = new_document("<faulty doc>")
    root += section(ids=("main-title",))
    root[-1] += title()
    root[-1][-1] += Text("Main Title")
    root[-1] += paragraph()
    root[-1][-1] += Text("Some text.")
    root[-1] += section(ids=("subtitle-a",))
    root[-1][-1] += title()
    root[-1][-1][-1] += Text("Subtitle A")
    root[-1][-1] += paragraph()
    root[-1][-1][-1] += Text("Some text.")
    root[-1] += section(ids=("subtitle-b", "subtitle-a"))
    root[-1][-1] += title()
    root[-1][-1][-1] += Text("Subtitle B")
    root[-1][-1] += paragraph()
    root[-1][-1][-1] += Text("Some text.")
    return root


def document_with_ambiguous_ids():
    """
    Create a document with ambiguous ids.

    :return: the document (document tree) with ambiguous ids
    """
    root = new_document("<faulty doc>")
    root += section(ids=("main-title",))
    root[-1] += title()
    root[-1][-1] += Text("Main Title")
    root[-1] += paragraph()
    root[-1][-1] += Text("See ")
    root[-1][-1] += reference(refid="para-a")
    root[-1][-1] += Text(" and ")
    root[-1][-1] += reference(refid="para-b")
    root[-1][-1] += Text(" for greater detail.")
    root[-1] += paragraph(ids=("para-a", "para-b"))
    root[-1][-1] += Text("Some text.")
    return root


def document_with_unprocessed_pending_ids():
    """
    Create a document with unprocessed pending ids.

    :return: the document (document tree) with unprocessed pending ids
    """
    root = new_document("<faulty doc>")
    root += section(ids=("main-title",))
    root[-1] += title()
    root[-1][-1] += Text("Main Title")
    root[-1] += paragraph()
    root[-1][-1] += Text("See ")
    root[-1][-1] += reference(refid="para-c")
    root[-1][-1] += Text(", ")
    root[-1][-1] += reference(refid="para-b")
    root[-1][-1] += Text(", and ")
    root[-1][-1] += reference(refid="para-a")
    root[-1][-1] += Text(" in case of further interest.")
    root[-1] += paragraph(ids=("para-b",))
    root[-1][-1] += Text("Some text.")
    return root


def document_with_illformed_reference():
    """
    Create a document with the ill-formed reference node.

    :return: the document (document tree) with the ill-formed reference node
    """
    root = new_document("<faulty doc>")
    root += section(ids=("main-title",))
    root[-1] += title()
    root[-1][-1] += Text("Main Title")
    root[-1] += paragraph()
    root[-1][-1] += Text("See ")
    root[-1][-1] += reference()
    root[-1][-1] += Text(" for further details.")
    return root


def document_with_target_nodes():
    """
    Create a document with target nodes.

    :return: the document (document tree) with target nodes
    """
    root = new_document("<target nodes>")
    root += target(refid="a")
    root += target(refid="b")
    root += paragraph()
    root[-1] += Text("Some text.")
    return root


def navbar_with_paragraphs():
    """
    Create a document with a navigation bar containing paragraphs.

    :return: the document (document tree) with the navigation bar containing
        paragraphs
    """
    root = new_document("<partial node>")
    root += compact_paragraph()
    root[-1]["navbar"] = True
    root[-1] += bullet_list()
    root[-1][-1] += list_item()
    root[-1][-1][-1] += paragraph()
    root[-1][-1][-1][-1] += reference(refuri="install.html")
    root[-1][-1][-1][-1][-1] += Text("Installation")
    root[-1][-1] += list_item()
    root[-1][-1][-1] += paragraph()
    root[-1][-1][-1][-1] += reference(refuri="")
    root[-1][-1][-1][-1][-1] += Text("User Guide")
    root[-1][-1] += list_item()
    root[-1][-1][-1] += paragraph()
    root[-1][-1][-1][-1] += reference(refuri="glossary.html")
    root[-1][-1][-1][-1][-1] += Text("Glossary")
    return root


class SimplifyListItemsTransform(SphinxTransform):
    """
    Delegate |paragraph|'s children to the |list_item|.

    Transform this:

    .. code:: xml

        <list_item>
          <paragraph>
            CHILDREN
          </paragraph>
        </list_item>

    into this:

    .. code:: xml

        <list_item>
          CHILDREN
        </list_item>
    """

    #: The |default priority| of this transform
    default_priority = 703

    __slots__ = ()

    def apply(self, **unused_kwargs):
        """
        Apply the transform.

        :param unused_kwargs: Key-value arguments
        """
        for node in self.document.findall(list_item):
            if len(node) != 1 or not isinstance(node[0], paragraph):
                continue
            para = node[0]
            node.replace(para, para.children)


class BrokenHtmlTranslator(HtmlTranslator):
    """|HtmlTranslator| with broken |HtmlTranslatorBase.start_tag| logic."""

    __slots__ = ()

    def visit_list_item(self, node):
        """
        Start the translation of the |list_item| document node.

        :param node: The |list item| document node
        """
        if self.context.in_scope(NAVBAR_SCOPE):
            return

        self.dump_inline_elements()
        self.start_tag("li", inline=1)
        node[LAST_CHAR_ATTR] = len(self.body) - 1
        self.context.push_node(node)


#: The definition of test cases
CASES = load_yaml(
    """
---
cases:
  - conflicting_ids
  - ambiguous_ids
  - unprocessed_pending_ids
  - ill-formed_reference
  - broken_body
  - missing_toctree
  - wrong_builder
  - target_nodes
  - paragraphs_in_navbar
  - navbar
  - heading
  - heading_no_permalinks
  - paragraph
  - bullet_list

conflicting_ids:
  input:
    type: doctree
    doctree: conflicting_ids

  output:
    type: html
    exception:
      type: ConflictingIdError
      args: >-
        Id `subtitle-a` from `<section ids="('subtitle-b',
        'subtitle-a')"><title>Subtitle B</title><paragraph>Some
        text.</paragraph></section>` already used

ambiguous_ids:
  input:
    type: doctree
    doctree: ambiguous_ids

  output:
    type: html
    exception:
      type: AmbiguousIdsError
      args: >-
        More than 1 ids (para-a, para-b) are trying to reference `<paragraph
        ids="('para-a', 'para-b')">Some text.</paragraph>`

unprocessed_pending_ids:
  input:
    type: doctree
    doctree: unprocessed_pending_ids

  output:
    type: html
    exception:
      type: UnprocessedPendingIdsError
      args: >-
        Unprocessed pending ids: para-a, para-c

ill-formed_reference:
  input:
    type: doctree
    doctree: ill-formed_reference

  output:
    type: html
    exception:
      type: MissingRefError
      args: >-
        `<reference/>` has no `refurl` or `refid`

broken_body:
  settings: broken_body_settings

  input:
    type: rst
    rst:
      - index: |
          * item

  output:
    type: html
    exception:
      type: BrokenBodyError
      args: >-
        Broken output/body content: Expected newline character

missing_toctree:
  input:
    type: rst
    rst:
      - index: |
          Some text.

  output:
    type: navbar
    exception:
      type: ThemeError
      args: >-
        Document has no toctree nodes

wrong_builder:
  settings: no_sphinx_spec_settings

  input:
    type: rst
    rst:
      - glossary: |
          Glossary
          ========

          Some text.

      - index: |
          Heading
          =======

          Some text.

          .. toctree::
             :caption: Table of Contents
             :maxdepth: 2

             glossary

  output:
    type: navbar
    exception:
      type: ThemeError
      args: >-
        `navbar()` can be only used within the `html` output context

target_nodes:
  input:
    type: doctree
    doctree: document_with_target_nodes

  output:
    type: raw
    raw: |
      <p>
        Some text.
      </p>

paragraphs_in_navbar:
  input:
    type: doctree
    doctree: navbar_with_paragraphs

  output:
    type: raw
    raw: |
      <a href="install.html">Installation</a>
      <a href="#">User Guide</a>
      <a href="glossary.html">Glossary</a>

navbar:
  input:
    type: rst
    rst:
      - installation: |
          Installation
          ============

          How to install.

      - user_guide: |
          User Guide
          ==========

          Welcome to our user guide.

      - reference_guide: |
          Reference Guide
          ===============

          All you need to know.

      - index: |
          Home
          ====

          Home page.

          .. toctree::
             :caption: Table of Contents
             :maxdepth: 2

             installation
             user_guide
             reference_guide

  output:
    type: navbar
    navbar:
      index: |
        <a href="installation.html">Installation</a>
        <a href="user_guide.html">User Guide</a>
        <a href="reference_guide.html">Reference Guide</a>
      user_guide: |
        <a href="installation.html">Installation</a>
        <a href="#">User Guide</a>
        <a href="reference_guide.html">Reference Guide</a>

heading:
  settings: heading_settings

  input:
    type: rst
    rst:
      - index: |
          Heading
          =======

          Some text.

  output:
    type: html
    html:
      index: |
        <section id="heading">
          <h1>Heading<a class="headerlink" href="#heading">&#x00B6;</a></h1>
          <div class="right-quote">
            Some description
          </div>
          <p>
            Some text.
          </p>
        </section>

heading_no_permalinks:
  settings: no_permalinks_settings

  input:
    type: rst
    rst:
      - index: |
          Heading
          =======

          Some text.

  output:
    type: html
    html:
      index: |
        <section id="heading">
          <h1>Heading</h1>
          <p>
            Some text.
          </p>
        </section>

paragraph:
  input:
    type: rst
    rst:
      - index: |
          .. |foo| replace:: bar
          ..
             Comment.

          .. compound::

             Line of text.

             Another line of text.

          Some text.

  output:
    type: html
    html:
      index: |
        <p>
          Line of text.
        </p>
        <p>
          Another line of text.
        </p>
        <p>
          Some text.
        </p>

bullet_list:
  input:
    type: rst
    rst:
      - index: |
          This is a list:

          * item A
          * item B
          * item C

  output:
    type: html
    html:
      index: |
        <p>
          This is a list:
        </p>
        <ul>
          <li>
            <p>
              item A
            </p>
          </li>
          <li>
            <p>
              item B
            </p>
          </li>
          <li>
            <p>
              item C
            </p>
          </li>
        </ul>
"""
)
#: Definitions of terms used in :const:`.CASES`
TERMS = {
    "conflicting_ids": document_with_conflicting_ids(),
    "ConflictingIdError": ConflictingIdError,
    "ambiguous_ids": document_with_ambiguous_ids(),
    "AmbiguousIdsError": AmbiguousIdsError,
    "unprocessed_pending_ids": document_with_unprocessed_pending_ids(),
    "UnprocessedPendingIdsError": UnprocessedPendingIdsError,
    "ill-formed_reference": document_with_illformed_reference(),
    "MissingRefError": MissingRefError,
    "broken_body_settings": {
        "abcdoctest_transforms": [SimplifyListItemsTransform],
        "abcdoctest_translator_class": BrokenHtmlTranslator,
    },
    "BrokenBodyError": BrokenBodyError,
    "ThemeError": ThemeError,
    "no_sphinx_spec_settings": {"abcdoctest_sphinx_spec": False},
    "document_with_target_nodes": document_with_target_nodes(),
    "navbar_with_paragraphs": navbar_with_paragraphs(),
    "heading_settings": {"description": "Some description"},
    "no_permalinks_settings": {
        "html_permalinks": False,
    },
}


class HelpersTestCase(TestCase):
    """Test case for auxiliary functions."""

    __slots__ = ()

    def test_node_source(self):
        """Test |node_source|."""
        self.assertIsNone(node_source(Element()))
        self.assertEqual(node_source(Element(), "foo"), "foo")
        self.assertEqual(node_source(Element(source="bar")), "bar")
        self.assertEqual(node_source(Element(source="bar"), "foo"), "bar")

    def test_is_partial_node(self):
        """Test |is_partial_node|."""
        self.assertFalse(is_partial_node(Element()))
        self.assertFalse(is_partial_node(Element(source="foo")))
        self.assertTrue(is_partial_node(Element(source=PARTIAL_NODE_NAME)))

    def test_is_index(self):
        """Test |is_index|."""
        config = make_config()
        self.assertFalse(is_index(Element(), config))
        self.assertFalse(is_index(Element(source="foo"), config))
        self.assertFalse(is_index(Element(source="./docs/api.rst"), config))
        self.assertFalse(is_index(Element(source="./docs/index"), config))
        self.assertFalse(is_index(Element(source="./docs/index.txt"), config))
        self.assertTrue(is_index(Element(source="./docs/index.rst"), config))

    def test_tag_attr(self):
        """Test |tag_attr|."""
        attrs = {
            "a_class": ("headerlink", "hidden"),
            "a_href": ("#foo",),
            "a_id": "foo",
            "foo": "bar",
        }
        self.assertEqual(
            tag_attr(attrs, "class"), ' class="headerlink hidden"'
        )
        self.assertEqual(tag_attr(attrs, "href"), ' href="#foo"')
        self.assertEqual(tag_attr(attrs, "id"), ' id="foo"')
        self.assertEqual(tag_attr(attrs, "foo"), "")
        self.assertEqual(tag_attr(attrs, "bar"), "")

    def test_check_ids(self):
        """Test |check_ids|."""
        with self.assertRaises(MissingIdsError) as cm:
            check_ids(Element())
        self.assertEqual(cm.exception.args[0], "`<Element/>` has no ids")

        with self.assertRaises(MissingIdsError) as cm:
            check_ids(Element(), throw=True)
        self.assertEqual(cm.exception.args[0], "`<Element/>` has no ids")

        self.assertFalse(check_ids(Element(), throw=False))

        with self.assertRaises(MissingIdsError) as cm:
            check_ids(Element(ids=()))
        self.assertEqual(
            cm.exception.args[0], '`<Element ids="()"/>` has no ids'
        )

        with self.assertRaises(MissingIdsError) as cm:
            check_ids(Element(ids=()), throw=True)
        self.assertEqual(
            cm.exception.args[0], '`<Element ids="()"/>` has no ids'
        )

        self.assertFalse(check_ids(Element(ids=()), throw=False))

        self.assertTrue(check_ids(Element(ids=("foo",))))
        self.assertTrue(check_ids(Element(ids=("foo",)), throw=True))
        self.assertTrue(check_ids(Element(ids=("foo",)), throw=False))

        self.assertTrue(check_ids(Element(ids=("foo", "bar"))))
        self.assertTrue(check_ids(Element(ids=("foo", "bar")), throw=True))
        self.assertTrue(check_ids(Element(ids=("foo", "bar")), throw=False))

    def test_get_id(self):
        """Test |get_id|."""
        with self.assertRaises(MissingIdsError) as cm:
            get_id(Element())
        self.assertEqual(cm.exception.args[0], "`<Element/>` has no ids")

        with self.assertRaises(MissingIdsError) as cm:
            get_id(Element(ids=()))
        self.assertEqual(
            cm.exception.args[0], '`<Element ids="()"/>` has no ids'
        )

        self.assertEqual(get_id(Element(ids=("foo",))), "foo")
        self.assertEqual(get_id(Element(ids=("foo", "bar"))), "foo")

    def test_ids2str(self):
        """Test |ids2str|."""
        self.assertEqual(ids2str(()), "")
        self.assertEqual(ids2str([]), "")
        self.assertEqual(ids2str(set()), "")

        self.assertEqual(ids2str(("foo",)), "foo")
        self.assertEqual(ids2str(["foo"]), "foo")
        self.assertEqual(ids2str({"foo"}), "foo")

        self.assertEqual(ids2str(("foo", "bar")), "bar, foo")
        self.assertEqual(ids2str(["foo", "bar"]), "bar, foo")
        self.assertEqual(ids2str({"foo", "bar"}), "bar, foo")


class ContextTestCaseBase(TestCase):
    """Base class for |Context| test cases."""

    __slots__ = ()

    def check_scope_stack(self, ctx):
        """
        Test |Context.check_scope_stack| on the empty stack.

        :param ctx: The |Context| instance
        """
        with self.assertRaises(ContextError) as cm:
            ctx.check_scope_stack()
        self.assertEqual(cm.exception.args, ("Scope stack is empty",))

    def check_node_stack(self, ctx):
        """
        Test |Context.check_node_stack| on the empty stack.

        :param ctx: The |Context| instance
        """
        with self.assertRaises(ContextError) as cm:
            ctx.check_node_stack()
        self.assertEqual(cm.exception.args, ("Node stack is empty",))

    def check_section_stack(self, ctx):
        """
        Test |Context.check_section_stack| on the empty stack.

        :param ctx: The |Context| instance
        """
        with self.assertRaises(ContextError) as cm:
            ctx.check_section_stack()
        self.assertEqual(cm.exception.args, ("Section stack is empty",))

    def push_scope_again(self, ctx, scope):
        """
        Test pushing the scope that is already on the stack.

        :param ctx: The |Context| instance
        :param scope: The scope to be pushed
        """
        with self.assertRaises(ContextError) as cm:
            ctx.push_scope(scope)
        self.assertEqual(
            cm.exception.args, (f"Scope `{scope}` is already on the stack",)
        )

    def push_node_again(self, ctx, node):
        """
        Test pushing the node that is already on the stack.

        :param ctx: The |Context| instance
        :param node: The node to be pushed
        """
        with self.assertRaises(ContextError) as cm:
            ctx.push_node(node)
        self.assertEqual(
            cm.exception.args, (f"Node `{node}` is already on the stack",)
        )

    def push_section_again(self, ctx, sect):
        """
        Test pushing the section that is already on the stack.

        :param ctx: The |Context| instance
        :param sect: The section to be pushed
        """
        with self.assertRaises(ContextError) as cm:
            ctx.push_section(sect)
        self.assertEqual(
            cm.exception.args, (f"Node `{sect}` is already on the stack",)
        )

    def push_wrong_section(self, ctx, sect):
        """
        Test pushing a wrong section.

        :param ctx: The |Context| instance
        :param sect: The section to be pushed
        """
        with self.assertRaises(ContextError) as cm:
            ctx.push_section(sect)
        self.assertEqual(
            cm.exception.args, (f"Node `{sect}` is not a section",)
        )

    def pop_on_empty_scope_stack(self, ctx, scope):
        """
        Test |Context.pop_scope| on the empty stack.

        :param ctx: The |Context| instance
        :param scope: The scope to be popped
        """
        with self.assertRaises(ContextError) as cm:
            ctx.pop_scope(scope)
        self.assertEqual(cm.exception.args, ("Scope stack is empty",))

    def pop_on_empty_node_stack(self, ctx, node):
        """
        Test |Context.pop_node| on the empty stack.

        :param ctx: The |Context| instance
        :param node: The node to be popped
        """
        with self.assertRaises(ContextError) as cm:
            ctx.pop_node(node)
        self.assertEqual(cm.exception.args, ("Node stack is empty",))

    def pop_on_empty_section_stack(self, ctx, sect):
        """
        Test |Context.pop_section| on the empty stack.

        :param ctx: The |Context| instance
        :param sect: The section to be popped
        """
        with self.assertRaises(ContextError) as cm:
            ctx.pop_section(sect)
        self.assertEqual(cm.exception.args, ("Section stack is empty",))

    def contribute_on_empty_node_stack(self, ctx, content):
        """
        Test |Context.contribute| on the empty stack.

        :param ctx: The |Context| instance
        :param content: The content to be contributed
        """
        with self.assertRaises(ContextError) as cm:
            ctx.contribute(content)
        self.assertEqual(cm.exception.args, ("Node stack is empty",))

    def get_section_level_on_empty_stack(self, ctx):
        """
        Test |Context.get_section_level| on the empty stack.

        :param ctx: The |Context| instance
        """
        with self.assertRaises(ContextError) as cm:
            ctx.get_section_level()
        self.assertEqual(cm.exception.args, ("Section stack is empty",))

    def get_section_id_on_empty_stack(self, ctx):
        """
        Test |Context.get_section_id| on the empty stack.

        :param ctx: The |Context| instance
        """
        with self.assertRaises(ContextError) as cm:
            ctx.get_section_id()
        self.assertEqual(cm.exception.args, ("Section stack is empty",))

    def get_section_id_on_wrong_section(self, ctx, sect):
        """
        Test |Context.get_section_id| on wrong section.

        :param ctx: The |Context| instance
        :param sect: The section
        """
        with self.assertRaises(MissingIdsError) as cm:
            ctx.get_section_id()
        self.assertEqual(cm.exception.args, (f"`{sect}` has no {IDS_ATTR}",))

    def pop_wrong_scope(self, ctx, wrong, current):
        """
        Test |Context.pop_scope| with wrong scope.

        :param ctx: The |Context| instance
        :param wrong: The wrong scope or the sequence of wrong scopes
        :param current: The current scope on the top of the stack
        """
        if isinstance(wrong, str):
            wrong = (wrong,)
        for scope in wrong:
            with self.assertRaises(ContextError) as cm:
                ctx.pop_scope(scope)
            self.assertEqual(
                cm.exception.args, (f"Expected `{scope}`, found `{current}`",)
            )

    def pop_wrong_node(self, ctx, wrong, current):
        """
        Test |Context.pop_node| with wrong node.

        :param ctx: The |Context| instance
        :param wrong: The wrong node or the sequence of wrong nodes
        :param current: The current node on the top of the stack
        """
        if isinstance(wrong, Element):
            wrong = (wrong,)
        for node in wrong:
            with self.assertRaises(ContextError) as cm:
                ctx.pop_node(node)
            self.assertEqual(
                cm.exception.args, (f"Expected `{current}`, given `{node}`",)
            )

    def pop_wrong_section(self, ctx, wrong, current):
        """
        Test |Context.pop_section| with wrong section.

        :param ctx: The |Context| instance
        :param wrong: The wrong section or the sequence of wrong sections
        :param current: The current section on the top of the stack
        """
        if isinstance(wrong, Element):
            wrong = (wrong,)
        for sect in wrong:
            with self.assertRaises(ContextError) as cm:
                ctx.pop_section(sect)
            self.assertEqual(
                cm.exception.args, (f"Expected `{current}`, given `{sect}`",)
            )

    def check_scopes(self, ctx, scopes, assertions):
        """
        Test |Context.in_scope| on multiple scopes.

        :param ctx: The |Context| instance
        :param scopes: The sequence of scopes
        :param assertions: The sequence of assertions about scopes

        :xarg:`assertions` and :xarg:`scopes` must be of the same length. An
        assertion is a single-letter character, either ``t`` for true or ``f``
        for false. ``t`` means that the scope from :xarg:`scopes` at the same
        index as ``t`` from :xarg:`assertions` must be present on the stack.
        ``f`` means the opposite.
        """
        for item in zip(scopes, assertions, strict=True):
            {"f": self.assertFalse, "t": self.assertTrue}[item[1]](
                ctx.in_scope(item[0])
            )

    def do_test_get_content(self, ctx, expected, *args, **kwargs):
        """
        Perform a |Context.get_content| test.

        :param ctx: The |Context| instance
        :param expected: The expected content
        :param args: Arguments to |Context.get_content|
        :param kwargs: Key-value arguments to |Context.get_content|
        """
        dump = kwargs.get("dump", False)
        if len(args) >= 1:
            dump = args[0]
        self.assertEqual(ctx.get_content(*args, **kwargs), expected)
        self.assertEqual(ctx.get_content(), "" if dump else expected)


class ContextTestCase(ContextTestCaseBase):
    """Test case for |Context|."""

    __slots__ = ("scopes", "nodes", "sections", "ctx")

    def setUp(self):
        """Set up the test."""
        #: The sequence of scopes
        self.scopes = ("scope_a", "scope_b", "scope_x")
        #: The sequence of nodes
        self.nodes = (Element(), Element(), Element())
        #: The sequence of sections
        self.sections = (
            section(ids=("ida_a", "id_b")),
            section(ids=("id_c",)),
            section(ids=()),
            section(),
        )
        #: The |Context| instance
        self.ctx = Context()

    def test_identity_check(self):
        """Test |Context.check_identity|."""
        Context.check_identity(self.nodes[0], self.nodes[0])
        with self.assertRaises(ContextError) as cm:
            Context.check_identity(Element(), Element())
        self.assertEqual(
            cm.exception.args, ("Expected `<Element/>`, given `<Element/>`",)
        )

    def test_empty_stack_ops(self):
        """Test operations on empty stacks."""
        self.check_scope_stack(self.ctx)
        self.check_scopes(self.ctx, self.scopes, "fff")
        self.pop_on_empty_scope_stack(self.ctx, self.scopes[0])
        self.check_scopes(self.ctx, self.scopes, "fff")

        self.check_node_stack(self.ctx)
        self.assertEqual(self.ctx.get_content(), "")
        self.pop_on_empty_node_stack(self.ctx, Element())
        self.assertEqual(self.ctx.get_content(), "")
        self.contribute_on_empty_node_stack(self.ctx, "word")
        self.assertEqual(self.ctx.get_content(), "")
        self.do_test_get_content(self.ctx, "", True)

        self.check_section_stack(self.ctx)
        self.pop_on_empty_section_stack(self.ctx, self.sections[0])
        self.get_section_level_on_empty_stack(self.ctx)
        self.get_section_id_on_empty_stack(self.ctx)

    def test_wrong_operations(self):
        """Test wrong operations on stacks."""
        self.ctx.push_scope(self.scopes[0])
        self.pop_wrong_scope(self.ctx, self.scopes[1:], self.scopes[0])
        self.push_scope_again(self.ctx, self.scopes[0])
        self.check_scopes(self.ctx, self.scopes, "tff")
        self.ctx.pop_scope(self.scopes[0])
        self.check_scope_stack(self.ctx)

        self.ctx.push_node(self.nodes[0])
        self.ctx.contribute("word")
        self.pop_wrong_node(self.ctx, self.nodes[1:], self.nodes[0])
        self.push_node_again(self.ctx, self.nodes[0])
        self.assertEqual(self.ctx.get_content(), "word")
        self.ctx.pop_node(self.nodes[0])
        self.check_node_stack(self.ctx)

        self.ctx.push_section(self.sections[0])
        self.push_wrong_section(self.ctx, Element())
        self.pop_wrong_section(self.ctx, self.sections[1:], self.sections[0])
        self.push_section_again(self.ctx, self.sections[0])
        self.assertEqual(self.ctx.get_section_level(), 1)
        self.assertEqual(
            self.ctx.get_section_id(), self.sections[0][IDS_ATTR][0]
        )
        self.ctx.push_section(self.sections[2])
        self.assertEqual(self.ctx.get_section_level(), 2)
        self.get_section_id_on_wrong_section(self.ctx, self.sections[2])
        self.ctx.push_section(self.sections[3])
        self.assertEqual(self.ctx.get_section_level(), 3)
        self.get_section_id_on_wrong_section(self.ctx, self.sections[3])
        self.ctx.pop_section(self.sections[3])
        self.ctx.pop_section(self.sections[2])
        self.ctx.pop_section(self.sections[0])
        self.check_section_stack(self.ctx)

    def test_scope_stack(self):
        """Test the scope stack."""
        self.ctx.push_scope(self.scopes[0])
        self.check_scopes(self.ctx, self.scopes, "tff")
        self.ctx.push_scope(self.scopes[1])
        self.check_scopes(self.ctx, self.scopes, "ttf")
        self.ctx.pop_scope(self.scopes[1])
        self.check_scopes(self.ctx, self.scopes, "tff")
        self.ctx.pop_scope(self.scopes[0])
        self.check_scope_stack(self.ctx)

    def test_node_stack(self):
        """Test the node stack."""
        self.ctx.push_node(self.nodes[0])
        self.assertEqual(self.ctx.get_content(), "")
        self.ctx.contribute("word_a")
        self.ctx.contribute("")
        self.assertEqual(self.ctx.get_content(), "word_a")
        self.ctx.push_node(self.nodes[1])
        self.assertEqual(self.ctx.get_content(), "")
        self.ctx.contribute("word_b")
        self.assertEqual(self.ctx.get_content(), "word_b")
        self.ctx.pop_node(self.nodes[1])
        self.assertEqual(self.ctx.get_content(), "word_a")
        self.ctx.contribute(", word_c")
        self.assertEqual(self.ctx.get_content(), "word_a, word_c")
        self.ctx.push_node(self.nodes[1])
        self.assertEqual(self.ctx.get_content(), "")
        self.ctx.pop_node(self.nodes[1])
        self.assertEqual(self.ctx.get_content(), "word_a, word_c")
        self.ctx.pop_node(self.nodes[0])
        self.check_node_stack(self.ctx)

    def test_get_content(self):
        """Test |Context.get_content|."""
        self.ctx.push_node(self.nodes[0])
        self.ctx.contribute("word_a")
        self.do_test_get_content(self.ctx, "word_a")
        self.do_test_get_content(self.ctx, "word_a", False)
        self.do_test_get_content(self.ctx, "word_a", dump=False)
        self.do_test_get_content(self.ctx, "word_a", dump=True)
        self.ctx.contribute("word_b")
        self.do_test_get_content(self.ctx, "word_b", True)
        self.ctx.pop_node(self.nodes[0])
        self.check_node_stack(self.ctx)

    def test_section_stack(self):
        """Test the section stack."""
        self.ctx.push_section(self.sections[0])
        self.assertEqual(self.ctx.get_section_level(), 1)
        self.assertEqual(
            self.ctx.get_section_id(), self.sections[0][IDS_ATTR][0]
        )
        self.ctx.push_section(self.sections[1])
        self.assertEqual(self.ctx.get_section_level(), 2)
        self.assertEqual(
            self.ctx.get_section_id(), self.sections[1][IDS_ATTR][0]
        )
        self.ctx.pop_section(self.sections[1])
        self.assertEqual(self.ctx.get_section_level(), 1)
        self.assertEqual(
            self.ctx.get_section_id(), self.sections[0][IDS_ATTR][0]
        )
        self.ctx.pop_section(self.sections[0])
        self.check_section_stack(self.ctx)


class HtmlTranslatorBaseTestCase(TestCase):
    """Test case for |HtmlTranslatorBase|."""

    __slots__ = ("document", "app", "patcher")

    def setUp(self):
        """Set up the test."""
        #: The test document
        self.document = new_document("<document>")
        #: The |Sphinx| application mock
        self.app = make_application()
        #: The module patcher
        self.patcher = ModulePatcher()

    def test_initialization(self):
        """Test |HtmlTranslatorBase.__init__|."""
        with self.patcher.patch():
            HtmlTranslatorBase(self.document, self.app.builder)
        self.assert_not_called(self.patcher.logger.setLevel)

    def test_debug_mode(self):
        """Test |HtmlTranslatorBase| with |abcdoc_debug| on."""
        self.app.config.abcdoc_debug = True
        with self.patcher.patch():
            HtmlTranslatorBase(self.document, self.app.builder)
        self.assert_called_with(self.patcher.logger.setLevel, logging.DEBUG)

    def test_getattr(self):
        """Test |HtmlTranslatorBase.__getattr__|."""
        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)

            self.assertEqual(translator.body_prefix, [])
            self.assertEqual(translator.body, [])

    def test_add_title(self):
        """Test |HtmlTranslatorBase.add_title|."""
        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)

            self.assertEqual(translator.title, [])
            translator.add_title("title A")
            self.assertEqual(translator.title, ["title A"])
            translator.add_title("title B")
            self.assertEqual(translator.title, ["title A", "title B"])

    def do_test_ship_body(self, translator, body, ship_empty, *args, **kwargs):
        """
        Perform a |HtmlTranslatorBase.ship_body| test.

        :param translator: The |HtmlTranslatorBase| instance
        :param body: The body to be shipped
        :param ship_empty: The flag telling to ship body even if the body is
            empty
        :param args: Arguments to |HtmlTranslatorBase.ship_body|
        :param kwargs: Key-value arguments to |HtmlTranslatorBase.ship_body|
        """
        for item in body:
            translator.body.append(item)
        if len(body) > 0 or ship_empty:
            translator.ship_body(*args, **kwargs)
        erase = kwargs.get("erase", False)
        if len(args) >= 1:
            erase = args[0]
        self.assertEqual(translator.fragment, body)
        self.assertEqual(translator.body, [] if erase else body)
        self.assertEqual(translator.astext(), "" if erase else "".join(body))
        translator.body.clear()
        translator.fragment.clear()

    def test_ship_body(self):
        """Test |HtmlTranslatorBase.ship_body|."""
        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)

            self.do_test_ship_body(translator, [], False)
            self.do_test_ship_body(translator, [], True)
            self.do_test_ship_body(
                translator, ["Hello", ", ", "World!"], False
            )
            self.do_test_ship_body(translator, ["abcdoc"], False, erase=False)
            self.do_test_ship_body(translator, ["abcdoc"], False, False)
            self.do_test_ship_body(translator, ["abcdoc"], False, erase=True)
            self.do_test_ship_body(translator, ["abcdoc"], False, True)

    def do_test_container_param(
        self, translator, func, expected, positional, **kwargs
    ):
        """
        Perform a test on a function with ``container`` parameter.

        :param translator: The |HtmlTranslatorBase| instance
        :param func: The callable object that has ``container=None`` as the
            second parameter in its signature
        :param expected: The expected result
        :param positional: The first argument to :xarg:`func`
        :param kwargs: Additional key-value arguments to :xarg:`func`
        """
        html_indent_level = translator.html_indent_level

        func(positional, **kwargs)
        self.assertEqual(translator.astext(), expected)
        translator.body.clear()

        translator.html_indent_level = html_indent_level
        func(positional, None, **kwargs)
        self.assertEqual(translator.astext(), expected)
        translator.body.clear()

        translator.html_indent_level = html_indent_level
        container = []
        func(positional, container, **kwargs)
        self.assertEqual("".join(container), expected)
        self.assertEqual(translator.astext(), "")

        translator.html_indent_level = html_indent_level
        func(positional, container=None, **kwargs)
        self.assertEqual(translator.astext(), expected)
        translator.body.clear()

        translator.html_indent_level = html_indent_level
        container = []
        func(positional, container=container, **kwargs)
        self.assertEqual("".join(container), expected)
        self.assertEqual(translator.astext(), "")

    def do_test_contribute(self, translator, expected, *args, **kwargs):
        """
        Perform a |HtmlTranslatorBase.contribute| test.

        :param translator: The |HtmlTranslatorBase| instance
        :param expected: The expected result
        :param args: Arguments to |HtmlTranslatorBase.contribute|
        :param kwargs: Key-value arguments to |HtmlTranslatorBase.contribute|
        """
        translator.contribute(*args, **kwargs)
        self.assertEqual(translator.astext(), expected)
        translator.body.clear()

    def test_contribute(self):
        """Test |HtmlTranslatorBase.contribute|."""
        text = (
            'This is a story about <em class="emphasize">long paragraph</em>'
            '. The paragraph was so <b class="bold large">long</b> so it had b'
            'een broken into multiple smaller <u class="underline">lines</u>.'
        )
        wrapped = (
            'This is a story about <em class="emphasize">long paragraph</em>'
            ". The paragraph\n"
            'was so <b class="bold large">long</b> so it had been broken int'
            "o multiple smaller\n"
            '<u class="underline">lines</u>.\n'
        )
        wrapped_indented = (
            '    This is a story about <em class="emphasize">long paragraph'
            "</em>. The paragraph\n"
            '    was so <b class="bold large">long</b> so it had been broken i'
            "nto multiple\n"
            '    smaller <u class="underline">lines</u>.\n'
        )

        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)
            translator.html_indent_level = 2

            self.do_test_container_param(
                translator, translator.contribute, text, text
            )
            self.do_test_container_param(
                translator, translator.contribute, wrapped, text, wrap=True
            )

            self.do_test_contribute(translator, "", "")
            self.do_test_contribute(translator, "", "", None, False)
            self.do_test_contribute(translator, "", "", None, True)
            self.do_test_contribute(translator, "", "", None, False, False)
            self.do_test_contribute(translator, "", "", None, False, True)
            self.do_test_contribute(translator, "", "", None, True, False)
            self.do_test_contribute(translator, "", "", None, True, True)

            self.do_test_contribute(translator, text, text)
            self.do_test_contribute(translator, text, text, None, False)
            self.do_test_contribute(
                translator, f"    {text}", text, None, True
            )
            self.do_test_contribute(translator, text, text, None, False, False)
            self.do_test_contribute(
                translator, wrapped, text, None, False, True
            )
            self.do_test_contribute(
                translator, f"    {text}", text, None, True, False
            )
            self.do_test_contribute(
                translator, wrapped_indented, text, None, True, True
            )

            self.do_test_contribute(translator, "", "", None, indent=False)
            self.do_test_contribute(translator, "", "", None, indent=True)
            self.do_test_contribute(translator, "", "", None, wrap=False)
            self.do_test_contribute(translator, "", "", None, wrap=True)
            self.do_test_contribute(
                translator, "", "", None, indent=False, wrap=False
            )
            self.do_test_contribute(
                translator, "", "", None, indent=False, wrap=True
            )
            self.do_test_contribute(
                translator, "", "", None, indent=True, wrap=False
            )
            self.do_test_contribute(
                translator, "", "", None, indent=True, wrap=True
            )

            self.do_test_contribute(translator, text, text, None, indent=False)
            self.do_test_contribute(
                translator, f"    {text}", text, None, indent=True
            )
            self.do_test_contribute(translator, text, text, None, wrap=False)
            self.do_test_contribute(translator, wrapped, text, None, wrap=True)
            self.do_test_contribute(
                translator, text, text, None, indent=False, wrap=False
            )
            self.do_test_contribute(
                translator, wrapped, text, None, indent=False, wrap=True
            )
            self.do_test_contribute(
                translator, f"    {text}", text, None, indent=True, wrap=False
            )
            self.do_test_contribute(
                translator,
                wrapped_indented,
                text,
                None,
                indent=True,
                wrap=True,
            )

    def do_test_tags(self, translator, expected, *args, **kwargs):
        """
        Perform tests on |HtmlTranslatorBase: tags|.

        :param translator: The |HtmlTranslatorBase| instance
        :param expected: The expected result
        :param args: Arguments to |HtmlTranslatorBase: tags|
        :param kwargs: Key-value arguments to |HtmlTranslatorBase: tags|
        """
        translator.start_tag(*args, **kwargs)
        translator.end_tag(*args, **kwargs)
        self.assertEqual(translator.astext(), expected)
        translator.body.clear()

    def test_tags(self):
        """Test |HtmlTranslatorBase: tags|."""
        p_indented = "    <p>\n    </p>\n"
        li_indented = "    <li></li>\n"
        em_inlined = "<em></em>"

        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)
            translator.html_indent_level = 2

            self.do_test_container_param(
                translator,
                translator.start_tag,
                '    <a id="id_A" class="headerlink hidden" href="#target">\n',
                "a",
                inline=0,
                a_href="#target",
                a_class=("headerlink", "hidden"),
                a_id="id_A",
            )
            self.do_test_container_param(
                translator, translator.end_tag, "    </p>\n", "p", inline=0
            )

            self.do_test_tags(translator, p_indented, "p")
            self.do_test_tags(translator, p_indented, "p", None, 0)
            self.do_test_tags(translator, p_indented, "p", inline=0)
            self.do_test_tags(translator, li_indented, "li", None, 1)
            self.do_test_tags(translator, li_indented, "li", inline=1)
            self.do_test_tags(translator, em_inlined, "em", None, 2)
            self.do_test_tags(translator, em_inlined, "em", inline=2)

            translator.start_tag("div")
            translator.start_tag("ul")
            translator.start_tag("li", inline=1)
            translator.start_tag("em", inline=2)
            translator.end_tag("em", inline=2)
            translator.end_tag("li", inline=1)
            translator.start_tag("li", inline=1)
            translator.start_tag("code", inline=2)
            translator.end_tag("code", inline=2)
            translator.end_tag("li", inline=1)
            translator.end_tag("ul")
            translator.end_tag("div")
            self.assertEqual(
                translator.astext(),
                (
                    "    <div>\n"
                    "      <ul>\n"
                    "        <li><em></em></li>\n"
                    "        <li><code></code></li>\n"
                    "      </ul>\n"
                    "    </div>\n"
                ),
            )

    def test_dispatching(self):
        """Test dispatching routines."""
        node = Element()
        node_attributes = {
            lvl: tuple(
                node_attribute_as_str(node, attr, lvl, prefix="\n")
                for attr in NODE_ATTRIBUTES
            )
            for lvl in (1, 2)
        }
        node_repr = {
            lvl: f'{"  " * (lvl - 1)}<Element{"".join(node_attributes[lvl])}>'
            for lvl in node_attributes
        }

        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)

            translator.dispatch_visit(node)
            with self.assertRaises(NotImplementedError) as cm:
                translator.dispatch_departure(node)
            self.assertEqual(
                cm.exception.args,
                (f"{type(translator)} departing unknown node type: Element",),
            )
            self.assertEqual(
                self.patcher.logs,
                [(("unknown node type: %r", node), {"location": node})],
            )

        self.app.config.abcdoc_debug = True
        self.patcher.logs.clear()
        with self.patcher.patch():
            translator = HtmlTranslatorBase(self.document, self.app.builder)

            translator.dispatch_visit(node)
            translator.dispatch_visit(node)
            translator.dispatch_departure(node)
            translator.dispatch_departure(node)
            self.assertEqual(
                self.patcher.logs,
                [
                    (("%s", node_repr[1]), {}),
                    (("unknown node type: %r", node), {"location": node}),
                    (("%s", node_repr[2]), {}),
                    (("unknown node type: %r", node), {"location": node}),
                    (("%s</%s>", "  ", "Element"), {}),
                    (("%s</%s>", "", "Element"), {}),
                ],
            )


class HtmlTranslatorTestCase(TestCase):
    """Test case for |HtmlTranslator|."""

    __slots__ = ()

    def do_case(self, case, **config_overrides):
        """
        Run the test given by :xarg:`case`.

        :param case: The test case definition
        :param config_overrides: Configuration overrides
        :raises ValueError: when the test case definition is ill-formed
        :raises KeyError: when the test case definition is ill-formed
        :raises TypeError: when the test case definition is ill-formed

        Every test case is a mapping that must contain ``input`` and
        ``output``. Additionally, it may contain ``settings``.

        ``input`` is a mapping that must contain ``type``. The possible values
        for ``type`` are ``doctree`` and ``rst``. If ``type`` is ``doctree``,
        then the ``input`` must also contain ``doctree``, holding a key to
        :const:`.TERMS` under which an input document tree can be found. If
        ``type`` is ``rst``, then the ``input`` must also contain ``rst``,
        holding a list of mappings where each of them is containing just one
        key, being a document name, under which the raw source of the document
        in the reStructuredText format is stored.

        ``output`` is a mapping that must contain ``type``. The possible values
        for ``type`` are ``html``, ``navbar``, and ``raw``. Additionally,
        ``output`` may also contain ``exception``.

        If ``exception`` is present in ``output``, it must be a mapping that
        must contain ``type`` and may contain ``args``. ``type`` is holding a
        key to :const:`.TERMS` under which the expected exception to be caught
        can be found. ``args`` is a list of expected arguments given to the
        caught exception when it was raised. ``args`` may also be a string,
        meaning that it is a list containing just that string. ``exception``
        has a priority over ``type``, meaning that if it is present the given
        exception with the given arguments must be raised by the test case.
        Note that in this case ``type`` may give a hint which part of the test
        case is about to raise the exception.

        If ``exception`` is not present in ``output``, then ``output`` must
        contain ``html``, ``navbar``, or ``raw`` if ``type`` is ``html``,
        ``navbar``, or ``raw``, respectively, where ``html`` and ``navbar``
        are mappings between a document name and the expected HTML code of the
        document or navigation bar, respectively, and ``raw`` holds a value of
        unspecified format that does not fit in any of previous cases. Note
        that ``raw`` is the only accepted ``output`` ``type`` for ``doctree``.

        ``settings`` holds a key to :const:`.TERMS` under which a :class:`dict`
        containing overrides for :xarg:`config_overrides` is stored.
        Configuration overrides are then updated with these ``settings`` before
        they are applied.

        The special settings that applies only to (unit) tests are:

        * ``abcdoctest_transforms`` specifies the additional :class:`list` of
          transforms
        * ``abcdoctest_translator_class`` specifies the translator class (the
          default is |HtmlTranslator|)
        * ``abcdoctest_sphinx_spec`` specifies whether to use Sphinx classes as
          ``spec`` argument to :class:`~unittest.mock.Mock` (default is
          :obj:`True`)
        """
        input_type = case["input"]["type"]
        output_type = case["output"]["type"]

        source = case["input"][input_type]
        if input_type == "doctree":
            source = TERMS[source]
        expected = case["output"].get(output_type, None)

        settings = case.get("settings", None)
        if settings is not None:
            config_overrides.update(TERMS[settings])

        def convert(source, **config_overrides):
            """
            Convert the source to the expected output.

            :param source: The source
            :param config_overrides: Configuration overrides
            :return: the expected output
            :raises ValueError: when the test case definition is ill-formed
            :raises KeyError: when the test case definition is ill-formed
            :raises TypeError: when the test case definition is ill-formed

            This is the auxiliary function internally used by
            :meth:`~HtmlTranslatorTestCase.do_case`.
            """
            result = None
            if input_type == "doctree":
                result = doctree2html(source, **config_overrides)
            elif input_type == "rst":
                result = rst2html(source, **config_overrides)
            else:
                raise ValueError(f"Unknown input type: {input_type}")
            if output_type in ("navbar", "html"):
                key = {"html": "body"}.get(output_type, output_type)
                result = {
                    name: result[name][key]
                    for name in (result if expected is None else expected)
                }
            if output_type == "navbar":
                result = {name: result[name]() for name in result}
            return result

        if "exception" in case["output"]:
            with self.assertRaises(
                TERMS[case["output"]["exception"]["type"]]
            ) as cm:
                convert(source, **config_overrides)
            args = case["output"]["exception"].get("args", None)
            if isinstance(args, str):
                args = [args]
            if args is not None:
                self.assertEqual(cm.exception.args, tuple(args))
        elif output_type in ("html", "navbar", "raw"):
            self.assertEqual(convert(source, **config_overrides), expected)
        else:
            raise ValueError(f"Unknown output type: {output_type}")

    def test_cases(self):
        """Run all tests specified in :const:`.CASES`."""
        for name in CASES["cases"]:
            self.do_case(CASES[name])
