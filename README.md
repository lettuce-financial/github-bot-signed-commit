# Signed Commits for GitHub Bots

GitHub users can (and should) signed their commits using normal git operations; GitHub bots cannot
because when they perform git operations, they do not have access to their signing key. GitHub
ensures that commits created by bots through their API will be signed, but constructing these
commits requires either managing lower level objects (trees, blobs) or using the GraphQL API,
which has challenging ergonomics from the CLI and can be extremely slow (e.g. over an hour) when
creating commits.

This project uses [GitPython](https://github.com/gitpython-developers/GitPython) to inspect a
local commit and recreate it remotely using [PyGitHub](https://github.com/PyGithub/PyGithub).


## Usage

### Prerequisites

It is assumed that you have an authorized GitHub app with permissions to write to the contents
of your target GitHub repository. You will need the `app id` and `private key` of this app
(and should be sure to keep the `private key` secret throughout any operations using this tool).

It is also assumed that you have a created a single, non-merge commit locally and wish to
recreate this commit remotely using the bot.

### Invocation

```sh
write-commit \
  --app-id <github-app-id> \
  --private-key <github-app-private-key> \
  --repo /path/to/repo \
  --ref <some-local-ref>
  --branch <some-remote-branch>
```

Note that the `GITHUB_APP_PRIVATE_KEY` environment variable can be used to pass the private
key without passing it as a commmand line argument.

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
