### Use an appropriate version of Python
FROM python:3.12-slim-bullseye@sha256:d33507ad3b58855b960d3cde870b01dd8ff17eed16c9a6bb8f7a1500eab10c89 AS python

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update -y && \
    apt-get -qq install -y git >/dev/null

### Install requirements
FROM python AS requirements

COPY requirements.txt /opt/project/
WORKDIR /opt/project
RUN --mount=type=cache,target=/root/.cache \
    pip install --disable-pip-version-check --requirement requirements.txt

### Install source and its dependencies
FROM requirements AS source

COPY pyproject.toml /opt/project/
COPY src /opt/project/src


### Define verify command
FROM source AS verify

ENV CI=1

RUN --mount=type=cache,target=/root/.cache \
    pip install --quiet --disable-pip-version-check --editable .[style,types,test]
COPY bin/verify* /opt/project/bin/

CMD ["/opt/project/bin/verify"]
