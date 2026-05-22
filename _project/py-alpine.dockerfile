ARG BASE_IMAGE
FROM ${BASE_IMAGE:-undefined}

WORKDIR /opt/word_games

ARG UID
ARG GUID

RUN addgroup -g $UID default_group \
    && adduser -D -u $GUID -G default_group default_user

RUN apk add --no-cache curl ca-certificates \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && uv --version

ARG PIP_VERSION
ARG UV_VERSION
RUN apk add pip==${PIP_VERSION} \
    && pip --version \
    && pip install uv==${UV_VERSION} \
    && uv --version


# Install dependencies. If the config variable IS_PROD=`true`, then
# install only default dependencies.
# 1. Install only dependencies
COPY pyproject.toml uv.lock ./
ARG IS_PROD
RUN if [ "${IS_PROD}" = "true" ]; then \
        uv sync --locked --no-dev --no-install-project; \
    else \
        uv sync --locked --no-install-project; \
    fi

# 2. Install the project
COPY . .
RUN if [ "${IS_PROD}" = "true" ]; then \
        uv sync --locked --no-dev \
        && rm pyproject.toml uv.lock; \
    else \
        uv sync --locked; \
    fi

USER root
RUN chown -R default_group:default_user .
USER default_user

CMD ["CMD must be overriden during container instantiation."]
