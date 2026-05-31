ARG BASE_IMAGE
FROM ${BASE_IMAGE:-undefined}

WORKDIR /opt/word_games

ARG UID
ARG GUID
RUN groupadd -g ${GUID} default_group \
    && useradd -m -u ${UID} -g default_group default_user

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

ARG PIP_VERSION
ARG UV_VERSION
RUN pip --version \
    && pip install --no-cache-dir pip==${PIP_VERSION} \
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

RUN chown -R ${UID}:${GUID} .
USER default_user

CMD ["CMD must be overriden during container instantiation."]
