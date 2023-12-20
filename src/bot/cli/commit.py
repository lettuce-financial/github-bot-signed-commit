from pathlib import Path

from click import Path as PathType
from click import command, option
from github.Auth import AppAuth

from ..local import read_commit
from ..remote import write_commit


@command()
@option(
    "--application-id",
    "--app-id",
    envvar="GITHUB_APP_ID",
    required=True,
)
@option(
    "--private-key",
    hidden=True,
    envvar="GITHUB_APP_PRIVATE_KEY",
    required=True,
)
@option(
    "--repo-path",
    "--repo",
    type=PathType(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
    required=True,
)
@option(
    "--ref",
    required=True,
)
def main(
    *,
    application_id: str,
    private_key: str,
    repo_path: Path,
    ref: str,
) -> None:
    auth = AppAuth(application_id, private_key)

    commit = read_commit(repo_path, ref)
    write_commit(auth, commit)
