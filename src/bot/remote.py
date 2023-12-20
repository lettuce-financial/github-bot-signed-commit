from github.Auth import Auth

from .dtos import Blob, Commit, Tree


def write_blob(auth: Auth, blob: Blob) -> None:
    # TODO: write blob
    pass


def write_tree(auth: Auth, tree: Tree) -> None:
    for tree in tree.trees:
        write_tree(auth, tree)

    for blob in tree.blobs:
        write_blob(auth, blob)

    # TODO: write tree


def write_commit(auth: Auth, commit: Commit) -> None:
    write_tree(auth, commit.tree)

    # TODO: write commit
