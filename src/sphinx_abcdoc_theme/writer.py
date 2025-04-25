#
# File:    ./src/sphinx_abcdoc_theme/writer.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-01-01 01:18:04 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""HTML writer."""

import collections.abc
import pathlib

from docutils.nodes import SkipChildren, section
from docutils.writers._html_base import Writer

from sphinx.errors import ThemeError
from sphinx.util.docutils import SphinxTranslator
from sphinx.util.logging import getLogger

from sphinx_abcdoc_theme.utils import (
    HTML_WORD_TOKENIZER_RE,
    SOURCE_ATTR,
    html_escape,
    indent_text,
    log_node_end,
    log_node_start,
    wrap as wrap_func,
)

HTML_INDENT_BASE = 0
HTML_INDENT_STRIDE = 2
MAX_HTML_HEADER_LEVEL = 6
PARTIAL_NODE_NAME = "<partial node>"


def node_source(node, default=None):
    if SOURCE_ATTR not in node:
        return default
    return node[SOURCE_ATTR]


def is_partial_node(node):
    return node_source(node, "") == PARTIAL_NODE_NAME


def is_index(document, config):
    source = node_source(document)
    if source is None:
        return False
    source_path = pathlib.Path(source).resolve()
    return (
        source_path.stem == config.root_doc
        and source_path.suffix in config.source_suffix
    )


def tag_attr(attrs, name):
    a_name = f"a_{name}"
    if a_name not in attrs:
        return ""
    value = attrs[a_name]
    if isinstance(value, collections.abc.Iterable) and not isinstance(
        value, str
    ):
        value = " ".join(value)
    return f' {name}="{value}"'


class MissingIdError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, node):
        """"""
        ThemeError.__init__(self, f"`{node}` has no ids")


def check_ids(node):
    """"""
    if not hasattr(node, "attributes") or "ids" not in node.attributes:
        raise MissingIdError(node)


class ConflictingIdError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, node, cid):
        """"""
        ThemeError.__init__(self, f"Id `{cid}` from `{node}` already used")


class AmbiguousIdsError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, node, ids):
        """"""
        ThemeError.__init__(
            self, f"More than 1 ids ({ids}) are trying to reference `{node}`"
        )


class UnprocessedPendingIdsError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, ids):
        """"""
        ThemeError.__init__(self, f"Unprocessed pending ids: {ids}")


class MissingRefError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, node):
        """"""
        ThemeError.__init__(self, f"`{node}` has no `refurl` or `refid`")


class BrokenBodyError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, detail):
        """"""
        ThemeError.__init__(self, f"Broken output/body content: {detail}")


class ContextError(ThemeError):
    """"""

    __slots__ = ()

    def __init__(self, message):
        """"""
        ThemeError.__init__(self, message)


class Context:
    """"""

    __slots__ = ("scope_stack", "node_stack", "section_stack", "node2fragment")

    def __init__(self):
        """"""
        self.scope_stack = []
        self.node_stack = []
        self.section_stack = []
        self.node2fragment = {}

    @staticmethod
    def check_identity(expected, given):
        """"""
        if expected is not given:
            raise ContextError(f"Expected `{expected}`, given `{given}`")

    def check_scope_stack(self):
        """"""
        if not self.scope_stack:
            raise ContextError("Scope stack is empty")

    def check_node_stack(self):
        """"""
        if not self.node_stack:
            raise ContextError("Node stack is empty")

    def check_section_stack(self):
        if not self.section_stack:
            raise ContextError("Section stack is empty")

    def push_scope(self, scope):
        self.scope_stack.append(scope)

    def pop_scope(self, scope):
        self.check_scope_stack()
        if self.scope_stack[-1] != scope:
            raise ContextError(
                f"Expected `{scope}`, found `{self.scope_stack[-1]}`"
            )
        self.scope_stack.pop(-1)

    def scope(self, scope):
        return scope in self.scope_stack

    def push_node(self, node):
        """"""
        self.node_stack.append(node)
        self.node2fragment[node] = []

    def pop_node(self, node):
        """"""
        self.check_node_stack()
        self.check_identity(node, self.node_stack[-1])
        self.node_stack.pop(-1)
        del self.node2fragment[node]

    def push_section(self, node):
        """"""
        if not isinstance(node, section):
            raise ContextError(f"Node `{node}` is not a section")
        self.push_node(node)
        self.section_stack.append(node)

    def pop_section(self, node):
        """"""
        self.check_section_stack()
        self.check_identity(node, self.section_stack[-1])
        self.section_stack.pop(-1)
        self.pop_node(node)

    def get_section_level(self):
        """"""
        self.check_section_stack()
        return len(self.section_stack)

    def get_section_id(self):
        """"""
        self.check_section_stack()
        top = self.section_stack[-1]
        check_ids(top)
        return top.attributes["ids"][0]

    def get_content_container(self):
        """"""
        self.check_node_stack()
        return self.node2fragment[self.node_stack[-1]]

    def contribute(self, obj):
        """"""
        self.get_content_container().append(str(obj))

    def get_content(self, dump=False):
        """"""
        if not self.node_stack:
            return ""
        container = self.get_content_container()
        content = "".join(container)
        if dump:
            container.clear()
        return content


class HtmlTranslatorBase(SphinxTranslator):
    """A custom HTML5 translator."""

    __slots__ = (
        "logger",
        "log_indent_level",
        "html_indent_level",
        "body",
        "fragment",
        "title",
    )

    def __init__(self, document, builder):
        """Initialize the HTML translator."""
        SphinxTranslator.__init__(self, document, builder)
        self.logger = getLogger(__name__)
        self.log_indent_level = 0
        self.html_indent_level = HTML_INDENT_BASE
        self.body = []
        self.fragment = []
        self.title = []

    def __getattr__(self, name):
        if name in Writer.visitor_attributes:
            return []
        return SphinxTranslator.__getattribute__(self, name)

    def add_title(self, title):
        self.title.append(title)

    def ship_body(self, erase=False):
        self.fragment.extend(self.body)
        if erase:
            self.body.clear()

    def astext(self):
        return "".join(self.body)

    def contribute(self, text, container=None, indent=False, wrap=False):
        if not text:
            return
        indent_level = self.html_indent_level if indent else 0
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

    def start_tag(self, name, container=None, inline=0, **attrs):
        self.contribute(f"<{name}", container=container, indent=(inline < 2))
        self.contribute(tag_attr(attrs, "id"), container=container)
        self.contribute(tag_attr(attrs, "class"), container=container)
        self.contribute(tag_attr(attrs, "href"), container=container)
        self.contribute(">", container=container)
        if inline == 0:
            self.contribute("\n", container=container)
            self.html_indent_level += 1

    def end_tag(self, name, container=None, inline=0):
        if inline == 0:
            self.html_indent_level -= 1
        self.contribute(
            f"</{name}>", container=container, indent=(inline == 0)
        )
        if inline < 2:
            self.contribute("\n", container=container)

    def dispatch_visit(self, node):
        """Dispatch the visit action."""
        if self.config.abcdoc_debug:
            log_node_start(node, self.log_indent_level, self.logger)
            self.log_indent_level += 1
        SphinxTranslator.dispatch_visit(self, node)

    def dispatch_departure(self, node):
        """Dispatch the departure action."""
        if self.config.abcdoc_debug:
            self.log_indent_level -= 1
            log_node_end(node, self.log_indent_level, self.logger)
        SphinxTranslator.dispatch_departure(self, node)

    def unknown_departure(self, node):
        """Report departure of unknown node."""
        if self.config.abcdoc_debug:
            return
        SphinxTranslator.unknown_departure(self, node)


class HtmlTranslator(HtmlTranslatorBase):
    """Custom HTML translator."""

    __slots__ = ("context", "document_root")

    def __init__(self, document, builder):
        """"""
        HtmlTranslatorBase.__init__(self, document, builder)
        self.context = Context()
        self.id2id = {}
        self.pending_ids = set()
        self.document_root = None
        self.is_partial_node = False

    def candidate_id(self, node):
        """"""
        check_ids(node)
        common = self.pending_ids & set(node.attributes["ids"])
        if len(common) > 1:
            raise AmbiguousIdsError(node, common)
        if len(common) == 1:
            cid = common.pop()
            self.pending_ids.remove(cid)
            return cid
        return node.attributes["ids"][0]

    def collect_ids(self, node):
        """"""
        id0 = self.candidate_id(node)
        for idn in node.attributes["ids"]:
            if idn in self.id2id:
                raise ConflictingIdError(node, idn)
            self.id2id[idn] = id0

    def get_id(self, node):
        """"""
        check_ids(node)
        return node.attributes["ids"][0]

    def translate_id(self, tid):
        """"""
        if tid not in self.id2id:
            self.pending_ids.add(tid)
            return tid
        return self.id2id[tid]

    def dump_inline_elements(self, container=None):
        content = self.context.get_content(True)
        if not content:
            return
        self.contribute(content, container=container, indent=True, wrap=True)

    def add_header_link(self, tid):
        """"""
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
