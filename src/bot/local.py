from pathlib import Path
from typing import Generator
from urllib.parse import urlparse

from git import Diff, Repo
from git.objects import Commit

from .dtos import Blob as BlobDTO
from .dtos import Commit as CommitDTO
from .dtos import Tree as TreeDTO

ROOT = Path()


def extract_repo_name(repo: Repo, remote: str = "origin") -> str:
    origin = repo.remote("origin")
    parsed_url = urlparse(origin.url)
    return parsed_url.path.rsplit(":", 1)[-1].removesuffix(".git")


def iter_blobs(item: Diff) -> Generator[BlobDTO, None, None]:
    match (item.change_type):
        case "A":
            # File added
            assert item.b_path is not None
            assert item.b_blob is not None

            yield BlobDTO(
                path=Path(item.b_path.lstrip("/")),
                sha=item.b_blob.hexsha,
            )
        case "D":
            # File deleted
            assert item.a_path is not None

            yield BlobDTO(
                path=Path(item.a_path.lstrip("/")),
                sha=None,
            )
        case "C":
            # File copied
            assert item.a_path is not None
            assert item.a_blob is not None
            assert item.b_path is not None
            assert item.b_blob is not None

            yield BlobDTO(
                path=Path(item.b_path.lstrip("/")),
                sha=item.b_blob.hexsha,
            )
        case "R":
            # File renamed
            assert item.a_path is not None
            assert item.a_blob is not None
            assert item.b_path is not None
            assert item.b_blob is not None

            yield BlobDTO(
                path=Path(item.a_path.lstrip("/")),
                sha=None,
            )
            yield BlobDTO(
                path=Path(item.b_path.lstrip("/")),
                sha=item.b_blob.hexsha,
            )
        case "M":
            # File modified
            assert item.b_path is not None
            assert item.b_blob is not None

            yield BlobDTO(
                path=Path(item.b_path.lstrip("/")),
                sha=item.b_blob.hexsha,
            )
        case "T":
            # File changed type (TODO)
            raise NotImplementedError("Diff type 'T' is not supported.")
        case _:
            raise ValueError(f"Unexpected diff type: {item.change_type}")


def build_trees(blobs: list[BlobDTO]) -> TreeDTO:
    trees: dict[Path, TreeDTO] = {}

    # Create the root tree
    root = trees[ROOT] = TreeDTO(path=ROOT)

    # Create all trees
    for blob in blobs:
        path = blob.path.parent
        while path != ROOT:
            trees.setdefault(path, TreeDTO(path))
            path = path.parent

    # Attach blobs to trees
    for blob in blobs:
        trees[blob.path.parent].blobs.append(blob)

    # Attach all trees to their parents
    for tree in trees.values():
        if tree.path == ROOT:
            continue

        trees[tree.path.parent].trees.append(tree)

    return root


def find_parent(commit: Commit) -> Commit:
    if not commit.parents:
        raise ValueError("Cannot create a repo's initial commit.")

    if len(commit.parents) > 1:
        raise ValueError("Cannot create a merge commit.")

    return commit.parents[0]


def extract_message(commit: Commit) -> str:
    if isinstance(commit.message, str):
        return commit.message
    else:
        return commit.message.decode("utf-8")


def read_repo(repo_path: Path) -> Repo:
    return Repo(repo_path)


def read_commit(repo: Repo, ref: str) -> CommitDTO:
    # Find the commit at the given ref in the local repo.
    commit = repo.commit(ref)

    # Compute the diff between the parent and this commit
    parent = find_parent(commit)
    diff = parent.diff(commit.hexsha)

    # Inspect the diff to create a commit
    blobs = [blob for diff_item in diff for blob in iter_blobs(diff_item)]

    root = build_trees(blobs)

    return CommitDTO(
        base_tree=parent.tree.hexsha,
        message=extract_message(commit),
        parents=[parent.hexsha],
        tree=root,
    )
