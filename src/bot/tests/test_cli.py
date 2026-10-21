from unittest.mock import MagicMock, patch

from click.testing import CliRunner
from pytest import mark

from bot.cli import write

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
def test_write_moves_the_branch_forward_unless_forced(
    flags: list[str], force: bool
) -> None:
    github = MagicMock()
    git_ref = github.get_repo.return_value.get_git_ref.return_value
    with (
        patch("bot.cli.authenticate_app", return_value=github),
        patch("bot.cli.read_repo"),
        patch("bot.cli.read_commit"),
        patch("bot.cli.write_commit") as write_commit,
    ):
        write_commit.return_value.sha = "abc"
        result = CliRunner().invoke(write, ARGS + flags)

    assert result.exit_code == 0, result.output
    git_ref.edit.assert_called_once_with("abc", force=force)
