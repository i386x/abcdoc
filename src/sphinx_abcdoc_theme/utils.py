#
# File:    ./src/sphinx_abcdoc_theme/utils.py
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2025-01-03 00:19:45 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#
"""
Utilities.

.. include:: defs.inc
"""

import abc
import re
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import logging
    from collections.abc import Iterator, Mapping, Sequence, Set
    from typing import Literal

    from sphinx_abcdoc_theme import Node, StrPath, Text
else:
    from docutils.nodes import Text

#: The name of ``caption`` attribute
CAPTION_ATTR: "Literal['caption']" = "caption"
#: The name of ``classes`` attribute
CLASSES_ATTR: "Literal['classes']" = "classes"
#: The name of ``ids`` attribute
IDS_ATTR: "Literal['ids']" = "ids"
#: The name of ``last_char`` attribute
LAST_CHAR_ATTR: "Literal['last_char']" = "last_char"
#: The name of ``names`` attribute
NAMES_ATTR: "Literal['names']" = "names"
#: The name of ``navbar`` attribute
NAVBAR_ATTR: "Literal['navbar']" = "navbar"
#: The name of ``refid`` attribute
REFID_ATTR: "Literal['refid']" = "refid"
#: The name of ``refuri`` attribute
REFURI_ATTR: "Literal['refuri']" = "refuri"
#: The name of ``source`` attribute
SOURCE_ATTR: "Literal['source']" = "source"

#: The name of ``attributes`` attribute
ATTRIBUTES_ATTR: str = "attributes"
#: The ``filename`` attribute name
FILENAME_ATTR: str = "filename"
#: The name of ``tagname`` attribute
TAGNAME_ATTR: str = "tagname"

#: The regular expression matching a non-empty sequence of white-space
#: characters
WS_RE: "re.Pattern[str]" = re.compile(r"\s+")
#: The regular expression matching either a non-empty sequence of white-space
#: characters or a non-empty sequence of non-white-space characters (a.k.a.
#: *words*)
WORD_TOKENIZER_RE: "re.Pattern[str]" = re.compile(r"\s+|\S+")
#: The regular expression matching one of:
#:
#: #. a non-empty sequence of white-space characters
#: #. a non-empty sequence of words and/or tags, where
#:
#:    * a *word* is a non-empty sequence of non-white-space characters
#:    * a *tag* is a sequence of characters between ``<`` and ``>``,
#:      including ``<`` and ``>``
#:
HTML_WORD_TOKENIZER_RE: "re.Pattern[str]" = re.compile(r"\s+|(<[^>]*>|\S+)+")

#: The mapping between Unicode code-points of special characters and their HTML
#: escape sequence
HTML_ESCAPE_TABLE: "Mapping[int, str]" = {
    ord('"'): "&quot;",
    ord("&"): "&amp;",
    ord("<"): "&lt;",
    ord(">"): "&gt;",
    ord("@"): "&#64;",
}

#: The number of spaces (ASCII 32) between two adjacent indentation levels in
#: log messages
LOG_INDENT_STRIDE: int = 2

#: The list of a |document node| attributes that should be included in debug
#: log messages
NODE_ATTRIBUTES: "Sequence[str]" = (
    ATTRIBUTES_ATTR,
    "autofootnote_refs",
    "autofootnote_start",
    "autofootnotes",
    "citation_refs",
    "citations",
    "current_line",
    "current_source",
    "footnote_refs",
    "footnotes",
    IDS_ATTR,
    "indirect_targets",
    LAST_CHAR_ATTR,
    "nameids",
    "nametypes",
    NAVBAR_ATTR,
    "rawsource",
    REFID_ATTR,
    "refids",
    "refnames",
    REFURI_ATTR,
    "substitution_names",
    "symbol_footnote_refs",
    "symbol_footnote_start",
    "symbol_footnotes",
    "toctree",
)
#: The set of |document node| attributes that are actually attribute
#: containers, holding other set of attributes together with their values.
#: Attributes from these containers should also be included in debug log
#: messages
NODE_ATTRIBUTES_CONTAINERS: "Set[str]" = {ATTRIBUTES_ATTR}


class FileAsset(metaclass=abc.ABCMeta):
    """
    An abstract base class for file assets.

    Provides the interface that every file asset must implement. Can be used
    with :func:`isinstance` and :func:`issubclass` to test whether the
    candidate class implements the interface.
    """

    __slots__ = ()

    @property
    @abc.abstractmethod
    def filename(self) -> "StrPath":
        """
        Return the file path.

        :return: the file path
        """
        return ""

    @classmethod
    def __subclasshook__(cls, subcls: "type[FileAsset]") -> bool:
        """
        Check whether :xarg:`subcls` is considered a subclass of this ABC.

        :param subcls: The candidate subclass
        :return: :obj:`True` if :xarg:`subcls` is considered a subclass of this
            abstract base class (ABC)
        """
        if cls is FileAsset:
            if any(
                FILENAME_ATTR in cast("Mapping[str, object]", supcls.__dict__)
                for supcls in subcls.__mro__
            ):
                return True
        return cast(bool, NotImplemented)


def html_escape(text: str) -> str:
    """
    Escape special characters.

    :param text: The text to be escaped
    :return: the escaped :xarg:`text`

    First, replace all sequences of white-space characters with a single space
    (ASCII 32). Then replace all special characters with the corresponding HTML
    escape sequences.
    """
    return WS_RE.sub(" ", text).translate(HTML_ESCAPE_TABLE)


def indentation(level: int, stride: int = 1) -> str:
    """
    Make an indentation.

    :param level: The indentation level
    :param stride: The indentation stride
    :return: the indentation

    The indentation is a sequence of spaces (ASCII 32) of the length
    :xarg:`stride` multiplied by :xarg:`level`. Note that :xarg:`stride` is a
    jump between two adjacent indentation levels.
    """
    return " " * stride * level


def indent_text(text: str, level: int, stride: int = 1) -> str:
    """
    Indent a text.

    :param text: The text to be indented
    :param level: The indentation level
    :param stride: The indentation stride
    :return: the indented :xarg:`text`

    Indent :xarg:`text` by :xarg:`level` times :xarg:`stride` spaces
    (ASCII 32).
    """
    return indentation(level, stride) + text


def tokenize(text: str, reobj: "re.Pattern[str]") -> "Iterator[str]":
    """
    Tokenize the text using the given regular expression.

    :param text: The text to be tokenized
    :param reobj: The compiled regular expression used for tokenizing
    :return: the sequence of tokens
    :raises ValueError: when :xarg:`text` cannot be tokenized with
        :xarg:`reobj`

    :xarg:`reobj` is used to split :xarg:`text` into matching tokens. Tokens
    consisting only from white-space characters are discarded from the output.
    """
    pos: int = 0
    while pos < len(text):
        matched: "re.Match[str] | None" = reobj.match(text, pos)
        if matched:
            result: str = matched.group().strip()
            if result:
                yield result
            pos += len(matched.group())
            continue
        raise ValueError(
            f"Cannot match `{text}` with `{reobj.pattern}` at {pos}"
        )


def wrap(
    text: str,
    limit: int = 79,
    indent: int = 0,
    tokenizer: "re.Pattern[str] | None" = None,
) -> "Iterator[str]":
    """
    Break text into lines of length close to the limit.

    :param text: The text to be wrapped
    :param limit: The requested line length, including line indentation
    :param indent: The indentation length of every line
    :param tokenizer: The compiled regular expression used to split
        :xarg:`text` into words (the default is :const:`.WORD_TOKENIZER_RE`)
    :return: the sequence of lines

    :xarg:`text` is broken into lines, where the length of each line plus
    :xarg:`indent` is as close to :xarg:`limit` as possible. :xarg:`tokenizer`
    controls how :xarg:`text` is broken into words from which a line is formed.
    A line break is never taken inside a word.
    """
    if tokenizer is None:
        tokenizer = WORD_TOKENIZER_RE
    line: str = ""
    for word in tokenize(text, tokenizer):
        nspaces: int = indent if len(line) == 0 else 1
        word = indent_text(word, nspaces)
        if limit - len(line) >= (len(word) + 1) // 2 or len(line) == 0:
            line += word
        else:
            yield f"{line}\n"
            line = indent_text(word.strip(), indent)
    if len(line) > 0:
        yield f"{line}\n"


def node_attribute_as_str(
    node: "Node",
    attr: str,
    level: int,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """
    Print the node attribute to a string.

    :param node: The document node
    :param attr: The attribute name
    :param level: The indentation level
    :param prefix: The prefix prepended to the output
    :param suffix: The suffix appended to the output
    :return: the string representation of the attribute

    Print :xarg:`attr`, together with its value, from :xarg:`node` to a string.
    If :xarg:`attr` is a container of attributes, print these attributes
    instead.

    Each attribute is printed as :xarg:`prefix`, followed by the indentation
    given by :xarg:`level` multiplied by :const:`.LOG_INDENT_STRIDE`, followed
    by the attribute name and attribute value, separated with ``": "``, and
    finally followed by :xarg:`suffix`.

    If :xarg:`attr` is not in :xarg:`node`, empty string is returned.
    """
    result: str = ""
    if not hasattr(node, attr):
        return result
    container: "Mapping[str, object]" = (
        cast("Mapping[str, object]", getattr(node, attr))
        if attr in NODE_ATTRIBUTES_CONTAINERS
        else {attr: cast(object, getattr(node, attr))}
    )
    for key, value in container.items():
        result += prefix + indent_text(
            f"{key}: {value}{suffix}", level, stride=LOG_INDENT_STRIDE
        )
    return result


def tagname(node: "Node") -> str:
    """
    Get the tag name associated with the node, if any.

    :param node: The document node
    :return: the tag name associated with :xarg:`node`

    If :xarg:`node` has no tag name associated with, use its class name.
    """
    if not hasattr(node, TAGNAME_ATTR) or node.tagname is None:
        return f"#node:{type(node).__name__}"
    return node.tagname


def log_node_start(
    node: "Node",
    level: int,
    logger: "logging.LoggerAdapter[logging.Logger]",
) -> None:
    """
    Open the node log.

    :param node: The document node
    :param level: The indentation level
    :param logger: The logger

    Write :xarg:`node` and its attributes to the logging output at the debug
    level, format and intend it properly so the children of :xarg:`node` can
    be logged afterwards.
    """
    message: str = indent_text(
        f"<{tagname(node)}", level, stride=LOG_INDENT_STRIDE
    )
    if isinstance(node, Text):
        message += f" {node}"
    for attr in NODE_ATTRIBUTES:
        message += node_attribute_as_str(node, attr, level + 1, prefix="\n")
    message += ">"
    logger.debug("%s", message)


def log_node_end(
    node: "Node",
    level: int,
    logger: "logging.LoggerAdapter[logging.Logger]",
) -> None:
    """
    Close the node log.

    :param node: The document node
    :param level: The indentation level
    :param logger: The logger

    Close :xarg:`node` and its children in the logging output at the debug
    level.
    """
    logger.debug(
        "%s</%s>", indentation(level, stride=LOG_INDENT_STRIDE), tagname(node)
    )
