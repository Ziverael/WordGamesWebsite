ARG DATABASE_IMAGE
FROM ${DATABASE_IMAGE:-undefined}

RUN apk add --no-cache \
    git \
    make \
    gcc \
    libc-dev \
    openssl \
    postgresql-dev \
    cmake \
    linux-headers \
    && openssl --version \
    && git --version \
    && make --version

RUN mkdir -p /etc/postgresql && \
    chown -R postgres:postgres /etc/postgresql
COPY _project/postgres/config/pg_hba.conf /etc/postgresql/pg_hba.conf
COPY _project/postgres/config/postgresql.conf /etc/postgresql/postgresql.conf
RUN chown postgres:postgres /etc/postgresql/pg_hba.conf /etc/postgresql/postgresql.conf && \
    chmod 600 /etc/postgresql/pg_hba.conf /etc/postgresql/postgresql.conf
