from logging import INFO
from logging import basicConfig as basic_config
from pathlib import Path

from click import Path as PathType
from click import command, option, secho

from .dtos import Tree
from .local import extract_repo_name, read_commit, read_repo
from .remote import authenticate_app, write_commit


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
    help="The path to the local git repository.",
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
    help="The local ref to read.",
    required=True,
)
def read(
    *,
    repo_path: Path,
    sha: str,
) -> None:
    """Read a commit from a local git repo and print it."""
    repo = read_repo(repo_path)
    commit = read_commit(repo, sha)

    secho(f"Commit: {commit.message}", fg="green")
    print_tree(commit.tree, Path())


@command()
@option(
    "--repo-path",
    help="The path to the local git repository.",
    type=PathType(
        exists=True,
        file_okay=False,
        dir_okay=True,
        path_type=Path,
    ),
    required=True,
)
@option(
    "--repo-name",
    help="The (fully qualified) name of the GitHub repo.",
)
@option(
    "--branch",
    help="The remote branch on which to add the generated commit.",
    required=True,
)
@option(
    "--ref",
    help="The local ref to recreate remotely.",
    required=True,
)
@option(
    "--app-id",
    envvar="GITHUB_APP_ID",
    help="The GitHub App's app id.",
    required=True,
    type=int,
)
@option(
    "--private-key",
    hidden=True,
    help="The GitHub App's private key",
    envvar="GITHUB_APP_PRIVATE_KEY",
    required=True,
)
def write(
    *,
    app_id: int,
    branch: str,
    private_key: str,
    repo_name: str | None,
    repo_path: Path,
    ref: str,
) -> None:
    """Read a commit from a local git repo and write it to GitHub."""
    basic_config(level=INFO)

    repo = read_repo(repo_path)
    repo_name = repo_name or extract_repo_name(repo)

    github = authenticate_app(app_id, private_key)
    repository = github.get_repo(repo_name)
    git_ref = repository.get_git_ref(f"heads/{branch}")

    commit = read_commit(repo, ref)
    git_commit = write_commit(repository, commit)
    git_ref.edit(git_commit.sha)
