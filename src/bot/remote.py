from logging import getLogger as get_logger

from github import Github, GithubIntegration
from github.Auth import AppAuth
from github.GitCommit import GitCommit
from github.GitTree import GitTree
from github.InputGitTreeElement import InputGitTreeElement
from github.Repository import Repository

from .dtos import Blob, Commit, Tree
from .enums import Mode, Type


def authenticate_app(application_id: int, private_key: str) -> Github:
    auth = AppAuth(application_id, private_key)
    integration = GithubIntegration(auth=auth)
    installation = integration.get_installations()[0]
    return installation.get_github_for_installation()  # type: ignore


def make_tree_blob_element(blob: Blob) -> InputGitTreeElement:
    if blob.sha:
        with blob.path.open() as infile:
            return InputGitTreeElement(
                path=str(blob.path),
                mode=Mode.FILE.value,
                type=Type.BLOB.value,
                content=infile.read(),
            )
    else:
        return InputGitTreeElement(
            path=str(blob.path),
            mode=Mode.FILE.value,
            type=Type.BLOB.value,
            sha=None,
        )


def make_tree_tree_element(tree: Tree, git_tree: GitTree) -> InputGitTreeElement:
    return InputGitTreeElement(
        path=str(tree.path),
        mode=Mode.SUBDIRECTORY.value,
        type=Type.TREE.value,
        sha=git_tree.sha,
    )


def write_tree(repo: Repository, tree: Tree, base_tree: GitTree) -> GitTree:
    logger = get_logger("GitTree")

    child_git_trees = [write_tree(repo, child, base_tree) for child in tree.trees]

    tree_items = [make_tree_blob_element(blob) for blob in tree.blobs] + [
        make_tree_tree_element(child, child_git_tree)
        for child, child_git_tree in zip(tree.trees, child_git_trees)
    ]

    logger.info(f"Creating git tree with {len(tree_items)} items from: {base_tree}")
    git_tree = repo.create_git_tree(
        tree=tree_items,
        base_tree=base_tree,
    )
    logger.info(f"Created git tree: {git_tree.sha}")
    return git_tree


def write_commit(repo: Repository, commit: Commit) -> GitCommit:
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
