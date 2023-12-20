from pathlib import Path

from click import Path as PathType
from click import command, option, secho
from github.Auth import AppAuth

from ..dtos import Tree
from ..local import read_commit
from ..remote import write_commit


def print_tree(tree: Tree, parent: Path, depth: int = 0) -> None:
    slash = "\\"
    space = " " * depth

    secho(f"{space}{slash} {tree.path.relative_to(parent)}", fg="green")

    for blob in tree.blobs:
        operation = "+" if blob.sha else "-"
        color = "cyan" if blob.sha else "red"
        secho(f"{space}|- ({operation}) {blob.path.relative_to(tree.path)}", fg=color)

    for child in tree.trees:
        print_tree(child, tree.path, depth + 1)


@command()
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
def read(
    *,
    repo_path: Path,
    ref: str,
) -> None:
    commit = read_commit(repo_path, ref)

    secho(f"Commit: {commit.message}", fg="green")
    print_tree(commit.tree, Path())


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
def write(
    *,
    application_id: str,
    private_key: str,
    repo_path: Path,
    ref: str,
) -> None:
    auth = AppAuth(application_id, private_key)

    commit = read_commit(repo_path, ref)
    write_commit(auth, commit)
