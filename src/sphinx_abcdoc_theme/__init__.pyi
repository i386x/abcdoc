#
# File:    ./src/sphinx_abcdoc_theme/__init__.pyi
# Author:  Jiří Kučera <sanczes AT gmail.com>
# Date:    2024-12-15 18:38:43 +0100
# Project: abcdoc: Tools for generating a documentation
#
# SPDX-License-Identifier: MIT
#

from collections.abc import Mapping, Sequence
from os import PathLike
from typing import ClassVar, Protocol, overload, runtime_checkable

from typing_extensions import TypeAlias

StrPath: TypeAlias = str | PathLike[str]

class NodeP(Protocol):
    parent: ElementP | None
    children: Sequence[NodeP]
    source: StrPath | None
    line: int | None
    tagname: ClassVar[str | None]
    document: DocumentP | None

class TextP(Protocol, NodeP): ...

class ElementP(Protocol, NodeP):
    attributes: Mapping[str, object]
    def __contains__(self, key: str | NodeP) -> bool: ...
    @overload
    def __getitem__(self, key: str) -> object: ...
    @overload
    def __getitem__(self, key: int) -> NodeP: ...

class DocumentP(Protocol, ElementP): ...

@runtime_checkable
class SectionP(Protocol, ElementP): ...

class ConfigP(Protocol):
    abcdoc_debug: bool
