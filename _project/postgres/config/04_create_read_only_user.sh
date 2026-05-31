#!/bin/bash
set -e

create_read_only_user () {
  _user="${1:?Missing user}"
  _password="${1:?Missing password}"
  # All databases despite POSTGRES_DB are passed as secrets
  psql -v ON_ERROR_STOP=1 --username "${_user}" <<-EOSQL
      CREATE USER ${_user}_read_only WITH PASSWORD '${_password}';

      GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO ${_user}_read_only;

      GRANT USAGE ON SCHEMA public TO ${_user}_read_only;
      GRANT SELECT ON ALL TABLES IN SCHEMA public TO ${_user}_read_only;
      ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO ${_user}_read_only;
EOSQL
}

echo "creating ${POSTGRES_USER}_read_only user..."
create_read_only_user "${POSTGRES_USER}" "${POSTGRES_PASSWORD}"
