### Use an appropriate version of Python
FROM python:3.14.8-bookworm@sha256:b3c121f5b6b446c964c6ea924d9a099e259b29d7b56df82729e33572a31eadcc AS python
ARG UV_VERSION=0.8.13
ARG UV_LIBC=musl

### Configure debian
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update -y && \
    apt-get -qq install -y git >/dev/null

### Install and configure uv
RUN UV_ARCHITECTURE=$(uname -m) && \
    wget --quiet https://github.com/astral-sh/uv/releases/download/${UV_VERSION}/uv-${UV_ARCHITECTURE}-unknown-linux-${UV_LIBC}.tar.gz && \
    tar -xf uv-${UV_ARCHITECTURE}-unknown-linux-${UV_LIBC}.tar.gz && \
    rm -f uv-${UV_ARCHITECTURE}-unknown-linux-${UV_LIBC}.tar.gz && \
    mv uv-${UV_ARCHITECTURE}-unknown-linux-${UV_LIBC}/* /usr/bin/ && \
    rmdir uv-${UV_ARCHITECTURE}-unknown-linux-${UV_LIBC}

### Install requirements
FROM python AS requirements

WORKDIR /opt/project
COPY pyproject.toml uv.lock /opt/project/

# Install the locked dependencies but not the project, whose source is not copied yet,
# so this layer is reused until pyproject.toml or uv.lock change. `--locked` fails the
# build when uv.lock no longer matches pyproject.toml, rather than quietly re-locking.
RUN --mount=type=cache,target=/root/.cache \
    uv sync --quiet --link-mode=copy --locked --no-install-project

### Install source and its dependencies
FROM requirements AS source

COPY pyproject.toml /opt/project/
COPY src /opt/project/src

### Define verify command
FROM source AS verify

ENV CI=1

# The environment below is synced from uv.lock with `--locked`, so it is the one to
# verify. This keeps the `uv run` in bin/verify* from syncing or re-locking on its own.
ENV UV_NO_SYNC=1

RUN --mount=type=cache,target=/root/.cache \
    uv sync --quiet --link-mode=copy --locked --extra style --extra types --extra test
COPY bin/verify* /opt/project/bin/

CMD ["/opt/project/bin/verify"]
