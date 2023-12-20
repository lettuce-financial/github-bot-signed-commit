"""Data transfer objects between git implementations."""
from dataclasses import dataclass

from .enums import Mode, Type


@dataclass(frozen=True)
class Blob:
    """A blob references file content."""

    path: str
    sha: str


@dataclass(frozen=True)
class Tree:
    """A tree references one or other trees or blobs."""

    path: str
    mode: Mode
    sha: str
    type: Type

    blobs: list[Blob]
    trees: list["Tree"]


@dataclass(frozen=True)
class Commit:
    """A commit references a message and a tree."""

    base_tree: str
    message: str
    parents: list[str]
    tree: Tree
