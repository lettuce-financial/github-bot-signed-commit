from pathlib import Path
from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from pytest import mark

from bot.cli.commit import main
from bot.dtos import Blob, Commit, Tree

ARGS = [
    "--repo-path",
    ".",
    "--repo-name",
    "o/r",
    "--branch",
    "b",
    "--ref",
    "HEAD",
    "--app-id",
    "1",
    "--private-key",
    "key",
]


@mark.parametrize(("flags", "force"), [([], False), (["--force"], True)])
def test_create_moves_the_branch_forward_unless_forced(
    flags: list[str], force: bool
) -> None:
    github = MagicMock()
    git_ref = github.get_repo.return_value.get_git_ref.return_value
    with (
        patch("bot.cli.commit.authenticate_app", return_value=github),
        patch("bot.cli.commit.read_repo"),
        patch("bot.cli.commit.read_commit"),
        patch("bot.cli.commit.write_commit") as write_commit,
    ):
        write_commit.return_value.sha = "abc"
        result = CliRunner().invoke(main, ["create", *ARGS, *flags])

    assert result.exit_code == 0, result.output
    git_ref.edit.assert_called_once_with("abc", force=force)


def test_retrieve_prints_the_commit_at_the_ref(tmp_path: Path) -> None:
    commit = Commit(
        base_tree="0000",
        message="Add foo",
        parents=["1111"],
        tree=Tree(
            path=Path(),
            blobs=[Blob(path=Path("foo.txt"), sha="2222")],
        ),
    )
    with (
        patch("bot.cli.commit.read_repo") as read_repo,
        patch("bot.cli.commit.read_commit", return_value=commit) as read_commit,
    ):
        result = CliRunner().invoke(
            main, ["retrieve", "--repo-path", str(tmp_path), "--ref", "abc"]
        )

    assert result.exit_code == 0, result.output
    read_repo.assert_called_once_with(tmp_path)
    read_commit.assert_called_once_with(read_repo.return_value, "abc")
    assert "Commit: Add foo" in result.output
    assert "(+) foo.txt" in result.output
