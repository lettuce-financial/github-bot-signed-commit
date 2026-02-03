### Use an appropriate version of Python
FROM python:3.14.2-bookworm@sha256:600efd165922696dafe6d8c5516ac5fd9c3d7e1923b7a9c4e2d6773a0da57921 AS python
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

COPY requirements.txt /opt/project/
WORKDIR /opt/project
RUN uv venv
RUN --mount=type=cache,target=/root/.cache \
    uv pip install --quiet --link-mode=copy --requirement requirements.txt

### Install source and its dependencies
FROM requirements AS source

COPY pyproject.toml /opt/project/
COPY src /opt/project/src

### Define verify command
FROM source AS verify

ENV CI=1

RUN --mount=type=cache,target=/root/.cache \
    uv pip install --quiet --link-mode=copy --editable .[style,types,test]
COPY bin/verify* /opt/project/bin/

CMD ["/opt/project/bin/verify"]
