from pathlib import Path
from unittest.mock import MagicMock

from git import Diff
from pytest import fixture

from bot.dtos import Blob
from bot.local import build_trees, iter_blobs


@fixture
def diff() -> Diff:
    item = MagicMock()
    item.a_path = "foo"
    item.a_blob.hexsha = "0000"
    item.b_path = "bar"
    item.b_blob.hexsha = "1111"
    return item


def test_iter_blobs_a(diff: Diff) -> None:
    diff.change_type = "A"

    blobs = list(iter_blobs(diff))
    assert len(blobs) == 1
    assert str(blobs[0].path) == "bar"
    assert blobs[0].sha is not None


def test_iter_blobs_d(diff: Diff) -> None:
    diff.change_type = "D"

    blobs = list(iter_blobs(diff))
    assert len(blobs) == 1
    assert str(blobs[0].path) == "foo"
    assert blobs[0].sha is None


def test_iter_blobs_c(diff: Diff) -> None:
    diff.change_type = "C"

    blobs = list(iter_blobs(diff))
    assert len(blobs) == 1
    assert str(blobs[0].path) == "bar"
    assert blobs[0].sha is not None


def test_iter_blobs_r(diff: Diff) -> None:
    diff.change_type = "R"

    blobs = list(iter_blobs(diff))
    assert len(blobs) == 2
    assert str(blobs[0].path) == "foo"
    assert blobs[0].sha is None
    assert str(blobs[1].path) == "bar"
    assert blobs[1].sha is not None


def test_iter_blobs_m(diff: Diff) -> None:
    diff.change_type = "M"

    blobs = list(iter_blobs(diff))
    assert len(blobs) == 1
    assert str(blobs[0].path) == "bar"
    assert blobs[0].sha is not None


def test_build_trees() -> None:
    blobs = [
        Blob(path=Path("foo/bar/baz.txt"), sha="0000"),
        Blob(path=Path("foo/qux.html"), sha="1111"),
    ]

    root = build_trees(blobs)

    assert root.path == Path()
    assert len(root.blobs) == 0
    assert len(root.trees) == 1

    foo = root.trees[0]
    assert foo.path == Path("foo")
    assert len(foo.blobs) == 1
    assert len(foo.trees) == 1

    qux = foo.blobs[0]
    assert qux.path == Path("foo/qux.html")
    assert qux.sha is not None

    bar = foo.trees[0]
    assert bar.path == Path("foo/bar")
    assert len(bar.blobs) == 1
    assert len(bar.trees) == 0

    baz = bar.blobs[0]
    assert baz.path == Path("foo/bar/baz.txt")
    assert baz.sha is not None
