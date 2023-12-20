from pathlib import Path

from git import Repo

from .dtos import Commit, Tree
from .enums import Mode, Type


def read_commit(repo_path: Path, ref: str) -> Commit:
    # Find the commit at the given ref in the local repo.
    repo = Repo(repo_path)
    commit = repo.commit(ref)

    if not commit.parents:
        raise ValueError("Cannot create a repo's initial commit.")

    if len(commit.parents) > 1:
        raise ValueError("Cannot create a merge commit.")

    parent = commit.parents[0]

    # Compute the diff between the commit and its parent
    diff = commit.diff(parent.hexsha)

    # Inspect the diff to create a commit
    for item in diff:
        # TODO
        pass

    if isinstance(commit.message, str):
        message = commit.message
    else:
        message = commit.message.decode("utf-8")

    return Commit(
        base_tree=parent.tree.hexsha,
        message=message,
        parents=[parent.hexsha],
        tree=Tree(
            path="",
            mode=Mode.SUBDIRECTORY,
            type=Type.TREE,
            blobs=[],
            trees=[],
            sha="",
        ),
    )
