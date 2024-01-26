"""Data transfer objects between git implementations."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Blob:
    """A blob references file content."""

    path: Path
    sha: str | None


@dataclass(frozen=True)
class Tree:
    """A tree references one or other trees or blobs."""

    path: Path

    blobs: list[Blob] = field(default_factory=list)
    trees: list["Tree"] = field(default_factory=list)


@dataclass(frozen=True)
class Commit:
    """A commit references a message and a tree."""

    base_tree: str
    message: str
    parents: list[str]
    tree: Tree
