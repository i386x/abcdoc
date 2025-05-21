#
# File:    ./src/sphinx_abcdoc_theme/writer.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-01-01 01:18:04 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
HTML writer.

.. |abcdoc_debug| replace:: ``abcdoc_debug``
.. |html_permalinks| replace:: ``html_permalinks``
.. |html_permalinks_icon| replace:: ``html_permalinks_icon``
"""

import pathlib
from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

from docutils.nodes import SkipChildren
from docutils.writers._html_base import Writer
from sphinx.errors import ThemeError
from sphinx.util.docutils import SphinxTranslator
from sphinx.util.logging import getLogger

from sphinx_abcdoc_theme.utils import (
    ATTRIBUTES_KW,
    HTML_WORD_TOKENIZER_RE,
    IDS_ATTR,
    SOURCE_ATTR,
    html_escape,
    indent_text,
    log_node_end,
    log_node_start,
)
from sphinx_abcdoc_theme.utils import wrap as wrap_func

if TYPE_CHECKING:
    import logging
    from collections.abc import (
        Mapping,
        MutableMapping,
        MutableSequence,
        MutableSet,
        Sequence,
        Set,
    )

    from docutils.nodes import Node, document
    from sphinx.builders import Builder
    from sphinx.config import Config

    from sphinx_abcdoc_theme import ConfigP, DocumentP, ElementP, NodeP
    from sphinx_abcdoc_theme import SectionP as section
    from sphinx_abcdoc_theme import StrPath
else:
    from docutils.nodes import section

#: Initial indentation level in the rendered HTML output
HTML_INDENT_BASE: int = 0
#: The number of spaces (ASCII 32) between two adjacent indentation levels in
#: the rendered HTML output
HTML_INDENT_STRIDE: int = 2
#: The maximal level of HTML headings
MAX_HTML_HEADER_LEVEL: int = 6
#: The name of a partial document node
PARTIAL_NODE_NAME: str = "<partial node>"


def node_source(
    node: "ElementP", default: "StrPath | None" = None
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
    return cast("StrPath", node[SOURCE_ATTR])


def is_partial_node(node: "ElementP") -> bool:
    """
    Test whether the document node is a partial node.

    :param node: The document node
    :return: :obj:`True` if :xarg:`node` is a partial node
    """
    return node_source(node, "") == PARTIAL_NODE_NAME


def is_index(document: "ElementP", config: "Config") -> bool:
    """
    Test whether the document is the root document.

    :param document: The document root node
    :param config: The Sphinx configuration
    :return: :obj:`True` if :xarg:`document` is the root document

    Root document is an alias for main or home page. For example,
    ``index.html`` is the root document, usually generated from ``index.rst``,
    when the output is set to be HTML.
    """
    source: "StrPath | None" = node_source(document)
    if source is None:
        return False
    source_path: "pathlib.Path" = pathlib.Path(source).resolve()
    return source_path.stem == cast(
        str, config.root_doc
    ) and source_path.suffix in cast("Mapping[str, str]", config.source_suffix)


def tag_attr(attrs: "Mapping[str, str | Sequence[str]]", name: str) -> str:
    """
    Convert attribute to a form used by a HTML tag.

    :param attrs: The container with attributes
    :param name: The attribute name
    :return: the string representing the attribute and its value suitable to be
        used directly inside a HTML tag

    Attributes stored in :xarg:`attrs` are prefixed with ``a_``. This helps to
    distinguish some attributes from the Python keywords, so attributes can be
    passed directly to a function in the form of key-value arguments.

    :xarg:`name` holds a name of the attribute from :xarg:`attrs` without
    ``a_`` prefix. An attribute value can be either a :class:`str` or a
    sequence of :class:`str` objects. In the latter case, strings are joined
    together with the space (ASCII 32) between them.

    The value returned is the space (ASCII 32), followed by :xarg:`name`,
    followed by ``=``, followed by the value enclosed between double quotes
    (``"``).

    When :xarg:`name` is not present in :xarg:`attrs`, the empty string is
    returned.

    Example::

        >>> def start_tag(name, **attrs):
        ...     return (
        ...         f"<{name}"
        ...         f'{tag_attr(attrs, "class")}'
        ...         f'{tag_attr(attrs, "href")}>'
        ...     )
        ...
        ...
        >>> start_tag("a", a_class=("headerlink", "hidden"), a_href="#index")
        '<a class="headerlink hidden" href="#index">'

    """
    a_name: str = f"a_{name}"
    if a_name not in attrs:
        return ""
    value: "str | Sequence[str]" = attrs[a_name]
    if isinstance(value, Iterable) and not isinstance(value, str):
        value = " ".join(value)
    return f' {name}="{value}"'


class MissingIdsError(ThemeError):
    """Signalizes that the node has no ``ids`` attribute."""

    __slots__ = ()

    def __init__(self, node: "NodeP") -> None:
        """
        Initialize the error.

        :param node: The document node
        """
        ThemeError.__init__(self, f"`{node}` has no {IDS_ATTR}")


def check_ids(node: "NodeP") -> None:
    """
    Check whether the node contains the ``ids`` attribute.

    :param node: The document node
    :raises .MissingIdsError: when :xarg:`node` does not contain ``ids``
        attribute
    """
    if IDS_ATTR not in cast(
        "Mapping[str, Sequence[str]]",
        getattr(node, ATTRIBUTES_KW, cast("Mapping[str, Sequence[str]]", {})),
    ):
        raise MissingIdsError(node)


def get_id(node: "NodeP") -> str:
    """
    Get the document node id.

    :param node: The document node
    :return: the first id on the list of ids of :xarg:`node`
    :raises ~.MissingIdsError: when :xarg:`node` has no ids
    """
    check_ids(node)
    return cast(
        "Sequence[str]", cast("ElementP", node).attributes[IDS_ATTR]
    )[0]


class ConflictingIdError(ThemeError):
    """Signalizes that the id from the node is already in use."""

    __slots__ = ()

    def __init__(self, node: "NodeP", cid: str) -> None:
        """
        Initialize the error.

        :param node: The document node
        :param cid: The conflicting id
        """
        ThemeError.__init__(self, f"Id `{cid}` from `{node}` already used")


class AmbiguousIdsError(ThemeError):
    """
    Signalizes that two or more ids are in a conflict.

    A conflict happens when two or more ids are trying to reference the same
    document node.
    """

    __slots__ = ()

    def __init__(self, node: "NodeP", ids: "Iterable[str]") -> None:
        """
        Initialize the error.

        :param node: The document node
        :param ids: The list of ids
        """
        ThemeError.__init__(
            self, f"More than 1 ids ({ids}) are trying to reference `{node}`"
        )


class UnprocessedPendingIdsError(ThemeError):
    """Signalizes there are ids that need to be processed."""

    __slots__ = ()

    def __init__(self, ids: "Iterable[str]") -> None:
        """
        Initialize the error.

        :param ids: The list of ids
        """
        ThemeError.__init__(self, f"Unprocessed pending ids: {ids}")


class MissingRefError(ThemeError):
    """Signalizes missing ``refurl`` or ``refid`` attributes in the node."""

    __slots__ = ()

    def __init__(self, node: "NodeP") -> None:
        """
        Initialize the error.

        :param node: The document node
        """
        ThemeError.__init__(self, f"`{node}` has no `refurl` or `refid`")


class BrokenBodyError(ThemeError):
    """Signalizes broken :attr:`~.HtmlTranslatorBase.body` fragment."""

    __slots__ = ()

    def __init__(self, detail: str) -> None:
        """
        Initialize the error.

        :param detail: The error detail
        """
        ThemeError.__init__(self, f"Broken output/body content: {detail}")


class ContextError(ThemeError):
    """Signalizes a :class:`.Context` error."""

    __slots__ = ()

    def __init__(self, message: str) -> None:
        """
        Initialize the error.

        :param message: The error message
        """
        ThemeError.__init__(self, message)


class Context:
    """HTML translator context."""

    #: The stack keeping scope names
    scope_stack: "MutableSequence[str]"
    #: The stack keeping document nodes
    node_stack: "MutableSequence[ElementP]"
    #: The stack keeping sections
    section_stack: "MutableSequence[section]"
    #: The mapping between node and output fragment
    node2fragment: "MutableMapping[ElementP, MutableSequence[str]]"

    __slots__ = ("scope_stack", "node_stack", "section_stack", "node2fragment")

    def __init__(self) -> None:
        """Initialize the context."""
        self.scope_stack = []
        self.node_stack = []
        self.section_stack = []
        self.node2fragment = {}

    @staticmethod
    def check_identity(expected: object, given: object) -> None:
        """
        Test whether two objects are identical.

        :param expected: The expected object
        :param given: The given object
        :raises .ContextError: when the given and the expected object are not
            identical
        """
        if expected is not given:
            raise ContextError(f"Expected `{expected}`, given `{given}`")

    def check_scope_stack(self) -> None:
        """
        Test whether the scope stack is not empty.

        :raises .ContextError: when the scope stack is empty
        """
        if not self.scope_stack:
            raise ContextError("Scope stack is empty")

    def check_node_stack(self) -> None:
        """
        Test whether the node stack is not empty.

        :raises .ContextError: when the node stack is empty
        """
        if not self.node_stack:
            raise ContextError("Node stack is empty")

    def check_section_stack(self) -> None:
        """
        Test whether the section stack is not empty.

        :raises .ContextError: when the section stack is empty
        """
        if not self.section_stack:
            raise ContextError("Section stack is empty")

    def push_scope(self, scope: str) -> None:
        """
        Push the scope.

        :param scope: The scope
        """
        self.scope_stack.append(scope)

    def pop_scope(self, scope: str) -> None:
        """
        Pop the scope.

        :param scope: The scope
        :raises .ContextError: when the scope stack is empty or its top does
            not match with :xarg:`scope`
        """
        self.check_scope_stack()
        if self.scope_stack[-1] != scope:
            raise ContextError(
                f"Expected `{scope}`, found `{self.scope_stack[-1]}`"
            )
        self.scope_stack.pop(-1)

    def in_scope(self, scope: str) -> bool:
        """
        Check if we operate within the given scope.

        :param scope: The given scope
        :return: :obj:`True` if we operate within the given scope
        """
        return scope in self.scope_stack

    def push_node(self, node: "ElementP") -> None:
        """
        Push the document node.

        :param node: The document node
        """
        self.node_stack.append(node)
        self.node2fragment[node] = []

    def pop_node(self, node: "ElementP") -> None:
        """
        Pop the document node.

        :param node: The document node
        :raises .ContextError: when the node stack is empty or its top does not
            match with :xarg:`node`
        """
        self.check_node_stack()
        self.check_identity(node, self.node_stack[-1])
        self.node_stack.pop(-1)
        del self.node2fragment[node]

    def push_section(self, node: "ElementP") -> None:
        """
        Push the section.

        :param node: The section node
        :raises .ContextError: when the document node is not a section node
        """
        if not isinstance(node, section):
            raise ContextError(f"Node `{node}` is not a section")
        self.push_node(node)
        self.section_stack.append(node)

    def pop_section(self, node: "ElementP") -> None:
        """
        Pop the section.

        :param node: The section node
        :raises .ContextError: when the section stack is empty or its top does
            not match with :xarg:`node`
        """
        self.check_section_stack()
        self.check_identity(node, self.section_stack[-1])
        self.section_stack.pop(-1)
        self.pop_node(node)

    def get_section_level(self) -> int:
        """
        Get the current section level.

        :return: the current section level, i.e. how deep we are nested in the
            document section hierarchy
        :raises .ContextError: when the section stack is empty
        """
        self.check_section_stack()
        return len(self.section_stack)

    def get_section_id(self) -> str:
        """
        Get the id of the current section.

        :return: the id of the current section
        :raises .ContextError: when the section stack is empty
        :raises .MissingIdsError: when the current section has no ids

        If the current section has more than one ids, the first one is
        returned.
        """
        self.check_section_stack()
        top: section = self.section_stack[-1]
        check_ids(top)
        return cast("Sequence[str]", top.attributes[IDS_ATTR])[0]

    def get_content_container(self) -> "MutableSequence[str]":
        """
        Get the content container associated with the current node.

        :return: the content container associated with the current node
        :raises .ContextError: when the node stack is empty
        """
        self.check_node_stack()
        return self.node2fragment[self.node_stack[-1]]

    def contribute(self, obj: object) -> None:
        """
        Contribute to the current content container.

        :param obj: The object to be contributed
        :raises .ContextError: when the node stack is empty, i.e. there is no
            content container

        Before contribution, :xarg:`obj` is converted to :class:`str`.

        The current content container is the sequential storage associated with
        the current document node.
        """
        self.get_content_container().append(str(obj))

    def get_content(self, dump: bool = False) -> str:
        """
        Get the content associated with the current document node.

        :param dump: The *also-clear-the-container* flag
        :return: the container content joined together as a one string

        If the node stack is empty (no container with a content to get), return
        the empty string. Otherwise, return the content of the container,
        associated with the current document node, concatenated together as a
        one string.

        If :xarg:`dump` is set to :obj:`True` then also clear (empty) the
        container.
        """
        if not self.node_stack:
            return ""
        container: "MutableSequence[str]" = self.get_content_container()
        content: str = "".join(container)
        if dump:
            container.clear()
        return content


class HtmlTranslatorBase(SphinxTranslator):
    """
    A customized HTML translator base.

    Extends Sphinx translator about:

    * logging traversed document nodes when |abcdoc_debug| option is enabled
    * making pretty HTML output
    """

    #: The logging facility
    logger: "logging.LoggerAdapter[logging.Logger]"
    #: The current indentation level in the logging output
    log_indent_level: int
    #: The current indentation level in the translator output
    html_indent_level: int
    #: The container holding constructed HTML body
    body: "MutableSequence[str]"
    #: The container holding the translator output (Sphinx uses it during HTML
    #: page assembling)
    fragment: "MutableSequence[str]"
    #: The container holding the document title (Sphinx uses it during HTML
    #: page assembling)
    title: "MutableSequence[str]"

    __slots__ = (
        "logger",
        "log_indent_level",
        "html_indent_level",
        "body",
        "fragment",
        "title",
    )

    def __init__(self, document: "document", builder: "Builder") -> None:
        """
        Initialize the HTML translator.

        :param document: The document root node
        :param builder: The Sphinx builder
        """
        SphinxTranslator.__init__(self, document, builder)
        self.logger = getLogger(__name__)
        self.log_indent_level = 0
        self.html_indent_level = HTML_INDENT_BASE
        self.body = []
        self.fragment = []
        self.title = []

    def __getattr__(self, name: str) -> object:
        """
        Get the translator attribute.

        :param name: The name of the attribute
        :return: the value of the attribute

        This function treats missing visitor attributes as empty so we do not
        need to define them here.
        """
        if name in Writer.visitor_attributes:
            return []
        return cast(object, SphinxTranslator.__getattribute__(self, name))

    def add_title(self, title: str) -> None:
        """
        Add the title or its part.

        :param title: The title or its fragment

        The final title is made up from :attr:`~.HtmlTranslatorBase.title` by
        concatenating of all its items together.
        """
        self.title.append(title)

    def ship_body(self, erase: bool = False) -> None:
        """
        Ship the body fragments.

        :param erase: The body container erase flag

        Append the content of :attr:`~.HtmlTranslatorBase.body` to
        :attr:`~.HtmlTranslatorBase.fragment`. Also clear the content of
        :attr:`~.HtmlTranslatorBase.body` if :xarg:`erase` is :obj:`True`.
        """
        self.fragment.extend(self.body)
        if erase:
            self.body.clear()

    def astext(self) -> str:
        """
        Return the content of :attr:`~.HtmlTranslatorBase.body` as a text.

        :return: the content of :attr:`~.HtmlTranslatorBase.body` concatenated
            together into the one string
        """
        return "".join(self.body)

    def contribute(
        self,
        text: str,
        container: "MutableSequence[str] | None" = None,
        indent: bool = False,
        wrap: bool = False,
    ) -> None:
        """
        Append the text to the given container.

        :param text: The text to be contributed
        :param container: The container used to store the contribution
        :param indent: The whether-to-indent flag
        :param wrap: The whether-to-wrap flag

        If :xarg:`container` is :obj:`None`, use
        :attr:`~.HtmlTranslatorBase.body`.

        If :xarg:`wrap` is :obj:`True`, :xarg:`text` is break into lines that
        fits the specified line length limit, including indentation. Currently,
        the line length limit is hard set to 79. The line breaks are chosen so
        the length of a line is as close to this number as possible.

        If :xarg:`indent` is :obj:`True`, :xarg:`text` and every line following
        is also indented. The indentation level is given by
        :attr:`~.HtmlTranslatorBase.html_indent_level`, the indentation stride
        by :const:`.HTML_INDENT_STRIDE`.
        """
        if not text:
            return
        indent_level: int = self.html_indent_level if indent else 0
        if container is None:
            container = self.body
        if wrap:
            for line in wrap_func(
                text,
                indent=indent_level * HTML_INDENT_STRIDE,
                tokenizer_re=HTML_WORD_TOKENIZER_RE,
            ):
                container.append(line)
        else:
            container.append(
                indent_text(text, indent_level, stride=HTML_INDENT_STRIDE)
            )

    def start_tag(
        self,
        name: str,
        container: "MutableSequence[str] | None" = None,
        inline: int = 0,
        **attrs: "str | Sequence[str]",
    ) -> None:
        """
        Start (open) a HTML tag.

        :param name: The HTML tag name
        :param container: The container where to store the output
        :param inline: The inline mode
        :param attrs: Additional tag attributes

        Make a tag with attributes given by :xarg:`attrs`. The currently
        supported attributes are ``id``, ``class``, and ``href`` (see
        :func:`.tag_attr` for the further details). The meaning of
        :xarg:`inline` is:

        * when 0 (no inline), the tag is put on a new line and it is properly
          indented plus the indentation level is increased so the following
          lines are also properly indented
        * when 1 (partially inline), the tag is put on a new line and it is
          properly indented but it is not ended with a new line character so
          the following content is appended right after the tag
        * when 2 (full inline), the tag is a part of some continuous piece of
          text, like paragraph

        If :xarg:`container` is :obj:`None`, :attr:`~.HtmlTranslatorBase.body`
        is used.
        """
        self.contribute(f"<{name}", container=container, indent=(inline < 2))
        self.contribute(tag_attr(attrs, "id"), container=container)
        self.contribute(tag_attr(attrs, "class"), container=container)
        self.contribute(tag_attr(attrs, "href"), container=container)
        self.contribute(">", container=container)
        if inline == 0:
            self.contribute("\n", container=container)
            self.html_indent_level += 1

    def end_tag(
        self,
        name: str,
        container: "MutableSequence[str] | None" = None,
        inline: int = 0,
    ) -> None:
        """
        End (close) the HTML tag.

        :param name: The HTML tag name
        :param container: The container where to store the output
        :param inline: The inline mode

        Make an enclosing tag and append it to :xarg:`container` or to
        :attr:`~.HtmlTranslatorBase.body` if :xarg:`container` is :obj:`None`.

        For the description of inline mode, see
        :meth:`~.HtmlTranslatorBase.start_tag`, except that in mode 0 the
        indentation level is restored and in other modes than 2 the output is
        terminated with a new line character.
        """
        if inline == 0:
            self.html_indent_level -= 1
        self.contribute(
            f"</{name}>", container=container, indent=(inline == 0)
        )
        if inline < 2:
            self.contribute("\n", container=container)

    def dispatch_visit(self, node: "Node") -> None:
        """
        Dispatch the visit action.

        :param node: The document node
        """
        if cast("ConfigP", self.config).abcdoc_debug:
            log_node_start(
                cast("NodeP", node), self.log_indent_level, self.logger
            )
            self.log_indent_level += 1
        SphinxTranslator.dispatch_visit(self, node)

    def dispatch_departure(self, node: "Node") -> None:
        """
        Dispatch the departure action.

        :param node: The document node
        """
        if cast("ConfigP", self.config).abcdoc_debug:
            self.log_indent_level -= 1
            log_node_end(
                cast("NodeP", node), self.log_indent_level, self.logger
            )
        SphinxTranslator.dispatch_departure(self, node)

    def unknown_departure(self, node: "Node") -> None:
        """
        Report a departure of unknown node.

        :param node: The document node
        """
        if cast("ConfigP", self.config).abcdoc_debug:
            return
        SphinxTranslator.unknown_departure(self, node)


class HtmlTranslator(HtmlTranslatorBase):
    """
    Custom HTML translator.

    This translator does not descend from the original Sphinx HTML5 translator.
    Instead it implements HTML5 translating process from scratch. The reason
    for this decision arose from need of few tweaks their implementation would
    lead into rewriting HTML5 translator from scratch in either way. Moreover,
    some of these tweaks, namely not depending on Sphinx CSS styles and class
    names (which, as stated by Sphinx upstream, are not promised to be stable
    at the end of the day), makes this translator backward-incompatible with
    the original HTML5 translator, resulting in some of the Sphinx
    configuration options not to be fully supported or omitted entirely. Also
    the translation of some of the document nodes is not implemented so far.

    What is currently supported:

    * HTML is rendered in human readable form to allow quick peek when opened
      with ordinary text editor (can be useful to find a quick answer for some
      issues)
    * translator is performing additional checks of cross-referencing at the
      single document level
    * with |abcdoc_debug| on it provides deep insight into translation process

    What is not supported or missing:

    * some document nodes are not translated (if such a node appears in the
      tree it stops translation with a failure)
    * some Sphinx options, both present and future, may have no effect
    * rendered HTML output does not work with the CSS styles provided by Sphinx
      and also it is not suitable for Sphinx-provided Jinja templates

    Definitions of Terms Used Later in the Documentation
    ----------------------------------------------------

    Given a list of nodes::

        <reference target="idA">

        <reference target="idD">

        <target#1 ids="idA idB">

        <target#2 ids="idC idD">

        <target#3 ids="idE idF">

        <reference target="idB">

        <reference target="idC">

        <reference target="idE">

    A *pending id* is an id that was used before it was defined. In the list of
    nodes above, pending ids are ``idA`` and ``idD``.

    The *candidate id* of some node is a pending id that is also an id of that
    node. If there is no such a pending id then it is the first id from the
    list of ids of that node. In the list of nodes above

    * ``target#1`` has ``idA`` as its candidate id because ``idA`` is a pending
      id and simultaneously it is also included in ``target#1`` ids list
    * ``target#2`` has ``idD`` as its candidate id for the same reason
    * ``target#3`` has ``idE`` as its candidate id because no id from
      ``target#3`` ids is a pending id and thus the candidate id is the first
      id from the ``target#3`` ids, which is ``idE``

    The idea behind candidate id is to select from the list of ids of some node
    the id (the candidate) that will appear in the rendered output. Once the
    candidate id of some node is selected the rest of the node ids are treated
    as aliases of the candidate id. As a consequence, the above list of nodes
    will be rendered as::

        <reference target="idA">

        <reference target="idD">

        <target#1 ids="idA">

        <target#2 ids="idD">

        <target#3 ids="idE">

        <reference target="idA">

        <reference target="idD">

        <reference target="idE">

    A situation like::

        <reference target="idA">

        <reference target="idB">

        <target#1 ids="idA idB">

    is treated as error because there are two candidate ids, ``idA`` and
    ``idB``, for one node. This cannot be fixed without deferring the output of
    the first two document nodes since at the time ``target#1`` node is
    processed both of the ``reference`` nodes were already sent to the output
    and thus their ``target`` cannot be fixed (this can be fixed by inserting
    ``<span id="...">`` in the proper place in HTML output but the approach
    here is to rather fix the document tree than put some hacks into the
    output).
    """

    #: The HTML translator context
    context: Context
    #: The id alias to the candidate id mapping
    id2id: "MutableMapping[str, str]"
    #: The set of pending ids that need to be processed
    pending_ids: "MutableSet[str]"
    #: The root node of the document tree
    document_root: "DocumentP | None"
    #: The flag telling whether the root of the document tree is a partial
    #: node. This means that the document is artificially fabricated and to be
    #: inserted into the main document
    is_partial_node: bool

    __slots__ = (
        "context",
        "id2id",
        "pending_ids",
        "document_root",
        "is_partial_node",
    )

    def __init__(self, document: "document", builder: "Builder") -> None:
        """
        Initialize the HTML translator.

        :param document: The document root node
        :param builder: The Sphinx builder
        """
        HtmlTranslatorBase.__init__(self, document, builder)
        self.context = Context()
        self.id2id = {}
        self.pending_ids = set()
        self.document_root = None
        self.is_partial_node = False

    def candidate_id(self, node: "NodeP") -> str:
        """
        Select the candidate id for the node.

        :param node: The document node
        :return: the candidate id
        :raises ~.MissingIdsError: when :xarg:`node` has no ids
        :raises ~.AmbiguousIdsError: when :xarg:`node` has more than one
            candidate id
        """
        check_ids(node)
        common: "MutableSet[str]" = cast(
            "MutableSet[str]",
            self.pending_ids
            & cast(
                "Set[str]",
                set(
                    cast(
                        "Iterable[str]",
                        cast("ElementP", node).attributes[IDS_ATTR],
                    )
                ),
            ),
        )
        if len(common) > 1:
            raise AmbiguousIdsError(node, common)
        if len(common) == 1:
            cid: str = common.pop()
            self.pending_ids.remove(cid)
            return cid
        return cast(
            "Sequence[str]", cast("ElementP", node).attributes[IDS_ATTR]
        )[0]

    def collect_ids(self, node: "NodeP") -> None:
        """
        Collect node ids.

        :param node: The document node
        :raises ~.MissingIdsError: when :xarg:`node` has no ids
        :raises ~.ConflictingIdError: when some id from :xarg:`node` has been
            already collected

        Collect all ids of :xarg:`node` and map them to its candidate id.
        """
        id0: str = self.candidate_id(node)
        for idn in cast(
            "Iterable[str]", cast("ElementP", node).attributes[IDS_ATTR]
        ):
            if idn in self.id2id:
                raise ConflictingIdError(node, idn)
            self.id2id[idn] = id0

    def translate_id(self, tid: str) -> str:
        """
        Translate the id alias to the candidate id.

        :param tid: The id alias
        :return: the candidate id

        If :xarg:`tid` has not been collected yet, add it to the set of pending
        ids and return its name as is.
        """
        if tid not in self.id2id:
            self.pending_ids.add(tid)
            return tid
        return self.id2id[tid]

    def dump_inline_elements(
        self, container: "MutableSequence[str] | None" = None
    ) -> None:
        """
        Dump inline elements from the context to the container.

        :param container: The container where to dump inline elements

        When :xarg:`container` is not specified,
        :attr:`~.HtmlTranslatorBase.body` is used.
        """
        content: str = self.context.get_content(True)
        if not content:
            return
        self.contribute(content, container=container, indent=True, wrap=True)

    def add_header_link(self, tid: "str | None") -> None:
        """
        Add a header link.

        :param tid: The target id

        Add a header link if |html_permalinks| is :obj:`True` and :xarg:`tid`
        is given. A header link icon can be configured via
        |html_permalinks_icon|.
        """
        if not self.config.html_permalinks or tid is None:
            return
        href = f"#{self.translate_id(tid)}"
        self.start_tag("a", inline=2, a_class="headerlink", a_href=href)
        self.contribute(self.config.html_permalinks_icon)
        self.end_tag("a", inline=2)

    def visit_bullet_list(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        self.dump_inline_elements()
        self.start_tag("ul")
        self.context.push_node(node)

    def depart_bullet_list(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        self.dump_inline_elements()
        self.context.pop_node(node)
        self.end_tag("ul")

    def visit_compact_paragraph(self, node):
        """"""
        if "navbar" in node and node["navbar"]:
            self.context.push_scope("navbar")

    def depart_compact_paragraph(self, node):
        """"""
        if "navbar" in node and node["navbar"]:
            self.context.pop_scope("navbar")

    def visit_document(self, node):
        """"""
        self.document_root = node
        self.is_partial_node = is_partial_node(node)

    def depart_document(self, node):
        """"""
        if len(self.pending_ids) > 0:
            raise UnprocessedPendingIdsError(self.pending_ids)
        self.ship_body()

    def visit_list_item(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        self.dump_inline_elements()
        self.start_tag("li")
        node["last_char"] = len(self.body) - 1
        self.context.push_node(node)

    def depart_list_item(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        inline = 0
        if node["last_char"] == len(self.body) - 1:
            # We have only pending inline elements
            container = []
            self.dump_inline_elements(container)
            # Now `container` should be populated with indented lines
            if len(container) <= 1:
                # The case `INDENT "<li>" INLINE_CDATA? "</li>" "\n"`
                inline = 1
                self.html_indent_level -= 1
                if self.body.pop(-1) != "\n":
                    raise BrokenBodyError("Expected newline character")
                if container:
                    container[0] = container[0].strip()
            self.contribute("".join(container))
        self.dump_inline_elements()
        self.context.pop_node(node)
        self.end_tag("li", inline=inline)

    def visit_paragraph(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        self.dump_inline_elements()
        self.start_tag("p")
        self.context.push_node(node)

    def depart_paragraph(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        self.dump_inline_elements()
        self.context.pop_node(node)
        self.end_tag("p")

    def visit_reference(self, node):
        """"""
        href = ""
        if "refuri" in node:
            href = node["refuri"] or "#"
        elif "refid" in node:
            href = f"#{self.translate_id(node['refid'])}"
        if not href:
            raise MissingRefError(node)

        if self.context.scope("navbar"):
            container = None
            inline = 1
        else:
            container = self.context.get_content_container()
            inline = 2

        self.start_tag("a", container=container, inline=inline, a_href=href)
        self.context.push_node(node)

    def depart_reference(self, node):
        """"""
        content = self.context.get_content(True)
        self.context.pop_node(node)

        if self.context.scope("navbar"):
            container = None
            inline = 1
        else:
            container = self.context.get_content_container()
            inline = 2

        self.contribute(content, container=container)
        self.end_tag("a", container=container, inline=inline)

    def visit_section(self, node):
        """"""
        self.dump_inline_elements()
        self.collect_ids(node)
        self.start_tag("section", a_id=self.get_id(node))
        self.context.push_section(node)

    def depart_section(self, node):
        """"""
        self.dump_inline_elements()
        self.context.pop_section(node)
        self.end_tag("section")

    def visit_substitution_definition(self, node):
        """"""
        raise SkipChildren

    def depart_substitution_definition(self, node):
        """"""

    def visit_target(self, node):
        """"""
        raise SkipChildren

    def depart_target(self, node):
        """"""

    def visit_title(self, node):
        """"""
        if self.context.scope("navbar"):
            raise SkipChildren

        self.dump_inline_elements()
        self.context.push_node(node)

    def depart_title(self, node):
        """"""
        if self.context.scope("navbar"):
            return

        title_text = self.context.get_content(True)
        self.context.pop_node(node)

        section_level = (
            self.context.get_section_level() if not self.is_partial_node else 1
        )
        if section_level > MAX_HTML_HEADER_LEVEL:
            section_level = MAX_HTML_HEADER_LEVEL
        if section_level == 1:
            self.add_title(title_text)
        section_id = (
            self.context.get_section_id() if not self.is_partial_node else None
        )

        self.start_tag(f"h{section_level}", inline=1)
        self.contribute(title_text)
        self.add_header_link(section_id)
        self.end_tag(f"h{section_level}", inline=1)
        if (
            section_level == 1
            and is_index(self.document_root, self.config)
            and self.config.description
        ):
            self.start_tag("div", a_class="right-quote")
            self.contribute(
                f"{html_escape(self.config.description)}\n", indent=True
            )
            self.end_tag("div")

    def visit_Text(self, node):
        """"""
        self.context.contribute(html_escape(node.astext()))

    def depart_Text(self, node):
        """"""
