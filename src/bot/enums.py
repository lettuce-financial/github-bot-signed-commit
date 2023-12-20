from enum import Enum, unique


@unique
class Mode(Enum):
    FILE = "100644"
    EXECUTABLE = "100755"
    SUBDIRECTORY = "040000"
    SUBMODULE = "160000"
    SYMLINK = "120000"


@unique
class Type(Enum):
    BLOB = "blob"
    TREE = "tree"
    COMMIT = "commit"
