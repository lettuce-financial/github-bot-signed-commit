from logging import INFO
from logging import basicConfig as basic_config
from pathlib import Path

from click import Path as PathType
from click import command, option, secho

from ..dtos import Tree
from ..local import extract_repo_name, read_commit, read_repo
from ..remote import authenticate_app, write_commit


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
    repo = read_repo(repo_path)
    commit = read_commit(repo, ref)

    secho(f"Commit: {commit.message}", fg="green")
    print_tree(commit.tree, Path())


@command()
@option(
    "--application-id",
    "--app-id",
    envvar="GITHUB_APP_ID",
    required=True,
    type=int,
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
    application_id: int,
    private_key: str,
    repo_path: Path,
    ref: str,
) -> None:
    basic_config(level=INFO)

    repo = read_repo(repo_path)
    repo_name = extract_repo_name(repo)

    github = authenticate_app(application_id, private_key)
    repository = github.get_repo(repo_name)

    commit = read_commit(repo, ref)
    git_commit = write_commit(repository, commit)

    secho(f"Created git commit: {git_commit.sha}", fg="green")
