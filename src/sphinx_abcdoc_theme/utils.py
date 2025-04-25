#
# File:    ./src/sphinx_abcdoc_theme/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-01-03 00:19:45 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""Utilities."""

import re

from docutils.nodes import Text

NAVBAR_ATTR = "navbar"
SOURCE_ATTR = "source"
IDS_ATTR = "ids"

WS_RE = re.compile(r"\s+")
WORD_TOKENIZER_RE = re.compile(r"\s+|\S+")
HTML_WORD_TOKENIZER_RE = re.compile(r"\s+|(<[^>]*>|\S+)+")

HTML_ESCAPE_TABLE = {
    ord('"'): "&quot;",
    ord("&"): "&amp;",
    ord("<"): "&lt;",
    ord(">"): "&gt;",
    ord("@"): "&#64;",
}

LOG_INDENT_STRIDE = 2

NODE_ATTRIBUTES = (
    "rawsource",
    "attributes",
    "current_source",
    "current_line",
    "indirect_targets",
    "substitution_names",
    "refnames",
    "refids",
    "nameids",
    "nametypes",
    IDS_ATTR,
    "footnote_refs",
    "citation_refs",
    "autofootnotes",
    "autofootnote_refs",
    "symbol_footnotes",
    "symbol_footnote_refs",
    "footnotes",
    "citations",
    "autofootnote_start",
    "symbol_footnote_start",
    "toctree",
    NAVBAR_ATTR,
)
NODE_ATTRIBUTES_CONTAINERS = {"attributes"}


def html_escape(text):
    return WS_RE.sub(" ", text).translate(HTML_ESCAPE_TABLE)


def indent(level, stride=1):
    return " " * stride * level


def indent_text(text, level, stride=1):
    return indent(level, stride) + text


def tokenize(text, reobj):
    pos = 0
    while pos < len(text):
        match = reobj.match(text, pos)
        if match:
            result = match.group().strip()
            if result:
                yield result
            pos += len(match.group())
            continue
        raise ValueError(
            f"Cannot match `{text}` with `{reobj.pattern}` at {pos}"
        )


def wrap(text, limit=79, indent=0, tokenizer_re=None):
    if tokenizer_re is None:
        tokenizer_re = WORD_TOKENIZER_RE
    line = ""
    for word in tokenize(text, tokenizer_re):
        nspaces = indent if len(line) == 0 else 1
        word = indent_text(word, nspaces)
        if limit - len(line) >= (len(word) + 1) // 2 or len(line) == 0:
            line += word
        else:
            yield f"{line}\n"
            line = indent_text(word.strip(), indent)
    if len(line) > 0:
        yield f"{line}\n"


def node_attribute_as_str(node, attr, level, preffix="", suffix=""):
    result = ""
    if not hasattr(node, attr):
        return result
    container = getattr(node, attr)
    if not attr in NODE_ATTRIBUTES_CONTAINERS:
        container = {attr: container}
    for key, value in container.items():
        result += preffix + indent_text(
            f"{key}: {value}{suffix}", level, stride=LOG_INDENT_STRIDE
        )
    return result


def log_node_start(node, level, logger):
    """Log a node."""
    message = indent_text(f"<{node.tagname}", level, stride=LOG_INDENT_STRIDE)
    if isinstance(node, Text):
        message += f" {node}"
    for attr in NODE_ATTRIBUTES:
        message += node_attribute_as_str(node, attr, level + 1, preffix="\n")
    message += ">"
    logger.debug("%s", message)


def log_node_end(node, level, logger):
    logger.debug(
        "%s</%s>", indent(level, stride=LOG_INDENT_STRIDE), node.tagname
    )
