from logging import getLogger as get_logger
from typing import Generator

from github import Github, GithubIntegration
from github.Auth import AppAuth
from github.GitCommit import GitCommit
from github.GitTree import GitTree
from github.InputGitTreeElement import InputGitTreeElement
from github.Repository import Repository

from .dtos import Blob, Commit, Tree
from .enums import Mode, Type


def authenticate_app(app_id: int, private_key: str) -> Github:
    """Create a Github instance with for a GitHub app (bot)."""
    auth = AppAuth(app_id, private_key)
    integration = GithubIntegration(auth=auth)
    installation = integration.get_installations()[0]
    return installation.get_github_for_installation()  # type: ignore


def make_tree_blob_element(blob: Blob) -> InputGitTreeElement:
    """Create a tree element for a blob."""
    if blob.sha:
        # Add
        with blob.path.open() as infile:
            return InputGitTreeElement(
                path=str(blob.path),
                mode=Mode.FILE.value,
                type=Type.BLOB.value,
                content=infile.read(),
            )
    else:
        # Remove
        return InputGitTreeElement(
            path=str(blob.path),
            mode=Mode.FILE.value,
            type=Type.BLOB.value,
            sha=None,
        )


def iter_tree_blob_element(tree: Tree) -> Generator[InputGitTreeElement, None, None]:
    """Collapse the tree structure into blob elements."""
    for child in tree.trees:
        yield from iter_tree_blob_element(child)

    for blob in tree.blobs:
        yield make_tree_blob_element(blob)


def write_tree(repo: Repository, tree: Tree, base_tree: GitTree) -> GitTree:
    """Write a git tree."""
    logger = get_logger("GitTree")

    tree_blob_elements = list(iter_tree_blob_element(tree))

    logger.info("Creating git tree")
    git_tree = repo.create_git_tree(
        tree=tree_blob_elements,
        base_tree=base_tree,
    )
    logger.info(f"Created git tree: {git_tree.sha}")
    return git_tree


def write_commit(repo: Repository, commit: Commit) -> GitCommit:
    """Write a git commit."""
    logger = get_logger("GitCommit")

    parent_git_commit = repo.get_git_commit(commit.parents[0])
    parent_git_tree = parent_git_commit.tree
    git_tree = write_tree(repo, commit.tree, parent_git_tree)

    logger.info(f"Creating git commit from tree: {git_tree.sha}")
    git_commit = repo.create_git_commit(
        message=commit.message,
        tree=git_tree,
        parents=[parent_git_commit],
    )
    logger.info(f"Created git commit: {git_commit.sha}")
    return git_commit
