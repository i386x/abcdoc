#
# File:    ./src/sphinx_abcdoc_theme/__init__.pyi
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-12-15 18:38:43 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#

from collections.abc import (
    Callable,
    Iterable,
    Iterator,
    Mapping,
    MutableSequence,
    Sequence,
)
from os import PathLike
from typing import ClassVar, Literal, Protocol, TypedDict, TypeVar, overload

from typing_extensions import TypeAlias

from sphinx_abcdoc_theme.utils import FileAsset

_N = TypeVar("_N", bound=Node)

StrPath: TypeAlias = str | PathLike[str]
ConfigRebuild: TypeAlias = Literal["", "env", "html"]

# To stop `mypy` complaining about `Any`, provide `Any`-free stubs (they need
# not to be complete, they are defined just enough to cover our use case). As
# `sphinx` depends on `docutils`

class FuncType(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...

class Values:
    env: BuildEnvironment

class LanguageModule:
    __name__: str

    labels: Mapping[str, str]
    bibliographic_fields: Mapping[str, str]
    author_separators: Sequence[str]

class Node:
    parent: Element | None
    children: Sequence[Node]
    source: StrPath | None
    line: int | None
    tagname: str | None
    document: Document | None

    def astext(self) -> str: ...
    def findall(
        self,
        condition: Callable[[_N], bool] | type[_N] | None = None,
        include_self: bool = True,
        descend: bool = True,
        siblings: bool = False,
        ascend: bool = False,
    ) -> Iterator[_N]: ...

class Text(Node, str): ...

class Element(Node):
    def __len__(self) -> int: ...
    def __contains__(self, key: str | Node) -> bool: ...
    def __iter__(self) -> Iterator[Node]: ...
    @overload
    def __getitem__(self, key: Literal["caption"]) -> str: ...
    @overload
    def __getitem__(self, key: Literal["classes"]) -> Sequence[str]: ...
    @overload
    def __getitem__(self, key: Literal["ids"]) -> Sequence[str]: ...
    @overload
    def __getitem__(self, key: Literal["last_char"]) -> int: ...
    @overload
    def __getitem__(self, key: Literal["names"]) -> MutableSequence[str]: ...
    @overload
    def __getitem__(self, key: Literal["navbar"]) -> bool: ...
    @overload
    def __getitem__(self, key: Literal["refid"]) -> str: ...
    @overload
    def __getitem__(self, key: Literal["refuri"]) -> str | None: ...
    @overload
    def __getitem__(self, key: Literal["source"]) -> StrPath | None: ...
    @overload
    def __getitem__(self, key: str) -> object: ...
    @overload
    def __getitem__(self, key: int) -> Node: ...
    @overload
    def __setitem__(self, key: Literal["caption"], item: str) -> None: ...
    @overload
    def __setitem__(
        self, key: Literal["classes"], item: Sequence[str]
    ) -> None: ...
    @overload
    def __setitem__(
        self, key: Literal["ids"], item: Sequence[str]
    ) -> None: ...
    @overload
    def __setitem__(self, key: Literal["last_char"], item: int) -> None: ...
    @overload
    def __setitem__(
        self, key: Literal["names"], item: MutableSequence[str]
    ) -> None: ...
    @overload
    def __setitem__(self, key: Literal["navbar"], item: bool) -> None: ...
    @overload
    def __setitem__(self, key: Literal["refid"], item: str) -> None: ...
    @overload
    def __setitem__(
        self, key: Literal["refuri"], item: str | None
    ) -> None: ...
    @overload
    def __setitem__(
        self, key: Literal["source"], item: StrPath | None
    ) -> None: ...
    @overload
    def __setitem__(self, key: str, item: object) -> None: ...
    @overload
    def __setitem__(self, key: int, item: Node) -> None: ...
    @overload
    def get(self, key: Literal["caption"]) -> str | None: ...
    @overload
    def get(self, key: Literal["caption"], default: str) -> str: ...
    @overload
    def get(self, key: Literal["classes"]) -> Sequence[str] | None: ...
    @overload
    def get(
        self, key: Literal["classes"], default: Sequence[str]
    ) -> Sequence[str]: ...
    @overload
    def get(self, key: Literal["ids"]) -> Sequence[str] | None: ...
    @overload
    def get(
        self, key: Literal["ids"], default: Sequence[str]
    ) -> Sequence[str]: ...
    @overload
    def get(self, key: Literal["last_char"]) -> int | None: ...
    @overload
    def get(self, key: Literal["last_char"], default: int) -> int: ...
    @overload
    def get(self, key: Literal["names"]) -> MutableSequence[str] | None: ...
    @overload
    def get(
        self, key: Literal["names"], default: MutableSequence[str]
    ) -> MutableSequence[str]: ...
    @overload
    def get(self, key: Literal["navbar"]) -> bool | None: ...
    @overload
    def get(self, key: Literal["navbar"], default: bool) -> bool: ...
    @overload
    def get(self, key: Literal["refid"]) -> str | None: ...
    @overload
    def get(self, key: Literal["refid"], default: str) -> str: ...
    @overload
    def get(self, key: Literal["refuri"]) -> str | None: ...
    @overload
    def get(self, key: Literal["refuri"], default: str) -> str: ...
    @overload
    def get(self, key: Literal["source"]) -> StrPath | None: ...
    @overload
    def get(self, key: Literal["source"], default: StrPath) -> StrPath: ...
    @overload
    def get(self, key: str) -> object | None: ...
    def extend(self, item: Iterable[Node]) -> None: ...
    def replace_self(self, new: Node | Sequence[Node]) -> None: ...

class Root: ...
class Structural: ...
class Body: ...
class General(Body): ...
class Section(Structural, Element): ...

class Document(Root, Element):
    settings: Values

    def note_implicit_target(
        self, target: Element, msgnode: Element | None = None
    ) -> None: ...

class Compound(General, Element): ...

class Transform:
    default_priority: ClassVar[int | None]

    document: Document
    startnode: Node | None
    language: LanguageModule

    def apply(self, **kwargs: object) -> None: ...

class NodeVisitor:
    def dispatch_visit(self, node: Node) -> None: ...
    def dispatch_departure(self, node: Node) -> None: ...
    def unknown_visit(self, node: Node) -> None: ...
    def unknown_departure(self, node: Node) -> None: ...

class PageContext(TypedDict):
    author: str
    description: str
    keywords: Sequence[str]
    navbar: Callable[[], str]
    fsfilter: Callable[
        [Sequence[FileAsset | StrPath], str], Iterator[FileAsset | StrPath]
    ]

def make_id(
    env: BuildEnvironment,
    document: Document,
    prefix: str = "",
    term: str | None = None,
) -> str: ...

class Config:
    abcdoc_debug: bool

    author: str
    description: str
    keywords: Sequence[str]
    root_doc: str
    source_suffix: Mapping[str, str]

    html_permalinks: bool
    html_permalinks_icon: str

class BuildEnvironment:
    config: Config | None

class SphinxTransform(Transform):
    app: Sphinx
    env: BuildEnvironment
    config: Config

class SphinxTranslator(NodeVisitor):
    config: Config
    settings: Values
    builder: Builder

    def __init__(self, document: Document, builder: Builder) -> None: ...

class Builder:
    name: ClassVar[str]

    app: Sphinx
    env: BuildEnvironment
    config: Config

class StandaloneHTMLBuilder(Builder):
    def render_partial(self, node: Node | None) -> Mapping[str, str]: ...

class Sphinx:
    config: Config
    env: BuildEnvironment
    builder: Builder

    @overload
    def connect(
        self,
        event: Literal["html-page-context"],
        callback: Callable[
            [Sphinx, str, str, PageContext, Document], str | None
        ],
        priority: int = 500,
    ) -> int: ...
    @overload
    def connect(
        self, event: str, callback: FuncType, priority: int = 500
    ) -> int: ...
    @overload
    def add_config_value(
        self,
        name: Literal["abcdoc_debug"],
        default: bool,
        rebuild: ConfigRebuild,
    ) -> None: ...
    @overload
    def add_config_value(
        self,
        name: Literal["description"],
        default: str,
        rebuild: ConfigRebuild,
    ) -> None: ...
    @overload
    def add_config_value(
        self,
        name: Literal["keywords"],
        default: Sequence[str],
        rebuild: ConfigRebuild,
    ) -> None: ...
    @overload
    def add_config_value(
        self, name: str, default: object, rebuild: ConfigRebuild
    ) -> None: ...
    def set_translator(
        self,
        name: str,
        translator_class: type[NodeVisitor],
        override: bool = False,
    ) -> None: ...
    def add_transform(self, transform: type[Transform]) -> None: ...
    def add_html_theme(self, name: str, theme_path: StrPath) -> None: ...

def global_toctree_for_doc(
    env: BuildEnvironment,
    docname: str,
    builder: Builder,
    collapse: bool = False,
    includehidden: bool = True,
    maxdepth: int = 0,
    titles_only: bool = False,
) -> Element | None: ...
