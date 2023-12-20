# Signed Commits for GitHub Bots

GitHub users can (and should) signed their commits using normal git operations; GitHub bots cannot
because when they perform git operations, they do not have access to their signing key. GitHub
ensures that commits created by bots through their API will be signed, but constructing these
commits requires either managing lower level objects (trees, blobs) or using the GraphQL API,
which has challenging ergonomics from the CLI and can be extremely slow (e.g. over an hour) when
creating commits.

This project uses [GitPython](https://github.com/gitpython-developers/GitPython) to inspect a
local commit and recreate it remotely using [PyGitHub](https://github.com/PyGithub/PyGithub).



## Docker

### Verification (CI)

 1. Build:

    ```sh
    docker build -t verify --target verify .
    ```

 2. Verify:

    ```sh
    docker run -it --rm verify
    ```
