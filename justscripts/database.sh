#!/usr/bin/sh
. justscripts/shell.sh
. justscripts/env.sh

_local_db_user="$(get_variable_from_dotenv_file "DATABASE_USER")"
_local_db_host="$(get_variable_from_dotenv_file "DATABASE_HOST")"

LOCAL_DB_CONNECTION_STRING="$(get_postgresql_connection_string \
    "${_local_db_user}" \
    "$(get_secret "db_user_password")" \
    "localhost" \
    "$(get_variable_from_dotenv_file "DATABASE_PORT")" \
    "" \
    "" \
)"

setup_tests_database(){
    echo_title "Setting up tests database..."
    _db_name="test_$(get_variable_from_dotenv_file "DATABASE_USER")"

    if [ "$(does_database_starts_with_test_prefix ${_db_name})" = "false" ];then
        echo_warning "Database name should starts with 'test_'"
        return 1
    fi
    if [ "$(does_database_exists "${_db_name}")" = "true" ];then
        echo_default "Database already exists. Dropping database..."
        drop_database "${_db_name}"
    fi
    create_database "${_db_name}"
    _db_user="test_$(get_variable_from_dotenv_file "DATABASE_USER")"
    drop_user "${_db_user}"
    create_user_with_password_for_database "${_db_user}" "$(get_secret "db_user_password")" "${_db_name}"
}

does_database_starts_with_test_prefix(){
    _db_name="${1:?Database name not passed}"
    [ "$(echo "${_db_name}" | grep -c "^test_")" = 1 ] && echo "true" || echo "false"
}

does_database_exists(){
    _db_name="${1:?Database name not passed}"
    [ "$(run_sql -At -c "SELECT 1 FROM pg_database WHERE datname='${_db_name}'")" = "1" ] && echo "true" || echo "false"
}

drop_database(){
    _db_name="${1:?Database name not passed}"
    echo_default "Dropping database ${_db_name}..."
    run_sql -o /dev/null <<-EOSQL
    DROP DATABASE ${_db_name};
EOSQL
}

create_database(){
    _db_name="${1:?Database name not passed}"
    echo_default "Creating database ${_db_name}..."
    run_sql -o /dev/null <<-EOSQL
    CREATE DATABASE ${_db_name};
EOSQL
}

drop_user(){
    _user="${1:?User not passed}"
    echo_default "Dropping user ${_user}..."
    run_sql -o /dev/null <<-EOSQL
DO \$\$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname='${_user}') THEN
        EXECUTE format('REVOKE USAGE, CREATE ON SCHEMA public FROM %I', '${_user}');
        EXECUTE format('DROP ROLE %I', '${_user}');
    END IF;
END
\$\$;
EOSQL

}

create_user_with_password_for_database(){
    _user="${1:?User not passed}"
    _pass="${2:?Password not passed}"
    _db_name="${3:?Database name not passed}"
    echo_default "Creating user ${_user} on database ${_db_name} and granting privileges..."
    run_sql -o /dev/null <<-EOSQL
    CREATE USER ${_user} WITH PASSWORD '${_pass}';
    GRANT CONNECT ON DATABASE ${_db_name} TO ${_user};
EOSQL
    setup_schema_for_user "${_db_name}" "${_user}" "public"
}

setup_schema_for_user(){
    _db_name="${1:?Database name not passed}"
    _user="${2:?User not passed}"
    _schema_name="${3:?Schema not passed}"
    run_sql <<- EOSQL
    \\c ${_db_name}
    CREATE SCHEMA IF NOT EXISTS ${_schema_name};
    GRANT USAGE, CREATE ON SCHEMA ${_schema_name} TO ${_user};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ${_schema_name} TO ${_user};
    GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ${_schema_name} TO ${_user};
    GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA ${_schema_name} TO ${_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${_schema_name} GRANT ALL PRIVILEGES ON TABLES TO ${_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${_schema_name} GRANT ALL PRIVILEGES ON SEQUENCES TO ${_user};
    ALTER DEFAULT PRIVILEGES IN SCHEMA ${_schema_name} GRANT ALL PRIVILEGES ON FUNCTIONS TO ${_user};
EOSQL
}

run_sql(){
    PGOPTIONS='--client-min-messages=warning' psql -X -q -v ON_ERROR_STOP=1 --pset pager=off ${LOCAL_DB_CONNECTION_STRING} "$@"
}
