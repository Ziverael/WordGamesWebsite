#!/usr/bin/env sh
. justscripts/shell.sh

create_or_update_dotenv(){
    REAL_DOTENV_TEMPLATE_MD5="$(md5sum .env.template | cut -d ' ' -f1 | cut -c -8)"
    SAVED_DOTENV_TEMPLATE_MD5=""
    [ -f .env ] && SAVED_DOTENV_TEMPLATE_MD5="$(grep -m 1 -e "^DOTENV_TEMPLATE_MD5=" .env | cut -d '=' -f2)"
    if [ "${REAL_DOTENV_TEMPLATE_MD5}" = "${SAVED_DOTENV_TEMPLATE_MD5}" ]
    then
        echo_title "Updating .env file..."
        echo_default "The .env ile is up to date. Skipped."
    fi

    if [ ! -f .env ]
    then
        echo_title "Creating .env file..."
        echo_default "Creating new .env file from .env.template file..."
        cp .env.template .env
        store_variable_in_dotenv_file "UID" "$(id -u)"
        store_variable_in_dotenv_file "GUID" "$(id -g)"
        store_variable_in_dotenv_file "APP_SECRET_KEY" "$(tr -dc 'A-Za-z0-9!?%=' < /dev/urandom | head -c 24)"
        _db_user="$(get_variable_from_dotenv_file "DATABASE_USER")"
        _db_pass="$(get_secret "db_user_password")"
        _db_host="$(get_variable_from_dotenv_file "DATABASE_HOST")"
        _db_port="$(get_variable_from_dotenv_file "DATABASE_PORT")"
        _db_name="$(get_variable_from_dotenv_file "DATABASE_USER")"
        store_variable_in_dotenv_file "DATABASE_CONNECTION_STRING" "$(get_postgresql_connection_string \
        "${_db_user}" \
        "${_db_pass}" \
        "${_db_host}" \
        "${_db_port}" \
        "${_db_name}" \
        "psycopg" \
        )"
    else
        echo_title "Updating .env file..."
        rm -f .local/.env.backup && cp .env .local/.env.backup && rm -f .env && cp .env.template .env
        restore_variable_in_dotenv_file UID
        restore_variable_in_dotenv_file GUID
        restore_variable_in_dotenv_file DATABASE_HOST
        restore_variable_in_dotenv_file DATABASE_PORT
        restore_variable_in_dotenv_file APP_SECRET_KEY
        restore_variable_in_dotenv_file DATABASE_CONNECTION_STRING
    fi
    echo_default "Storing .env.template md5 sum..."
    sed_inplace "s|^DOTENV_TEMPLATE_MD5=.*$|DOTENV_TEMPLATE_MD5=${REAL_DOTENV_TEMPLATE_MD5}|g" .env
}

store_variable_in_dotenv_file () {
    VARIABLE_NAME="${1:?}"
    VARIABLE_VALUE="${2:?}"
    echo_default "Storing ${VARIABLE_NAME} default value..."
    sed_inplace "s|^${VARIABLE_NAME}=.*$|${VARIABLE_NAME}=${VARIABLE_VALUE}|g" .env
}

restore_variable_in_dotenv_file () {
    VARIABLE_NAME="${1:?}"
    VARIABLE_VALUE=""
    [ -f .local/.env.backup ] && VARIABLE_VALUE="$(grep -m 1 -e "^${VARIABLE_NAME}=" .local/.env.backup | cut -d '=' -f2)"
    VARIABLE_VALUE_IN_DOTENV_TEMPLATE="$(grep -m 1 -e "^${VARIABLE_NAME}=" .env.template | cut -d '=' -f2)"
    if [ -n "${VARIABLE_VALUE}" ] && [ "${VARIABLE_VALUE}" != "${VARIABLE_VALUE_IN_DOTENV_TEMPLATE}" ]
    then
        echo_default "Restoring ${VARIABLE_NAME} value..."
        sed_inplace "s|^${VARIABLE_NAME}=.*$|${VARIABLE_NAME}=${VARIABLE_VALUE}|g" .env
    fi
}

get_variable_from_dotenv_file () {
    VARIABLE_NAME="${1:?}"
    if [ ! -f .env ]
    then
        TARGET_ENV_FILE=".env.template"
    else
        TARGET_ENV_FILE=".env"
    fi
    VARIABLE_VALUE="$(grep -m 1 -e "^${VARIABLE_NAME}=" "${TARGET_ENV_FILE}" | cut -d '=' -f2)"
    VARIABLE_VALUE_WITHOUT_TRAILING_QUOTES="${VARIABLE_VALUE%\"}"
    VARIABLE_VALUE_WITHOUT_LEADING_QUOTES="${VARIABLE_VALUE_WITHOUT_TRAILING_QUOTES#\"}"
    echo "${VARIABLE_VALUE_WITHOUT_LEADING_QUOTES}"
}


get_postgresql_connection_string(){
    _user="${1:?Missing user}"
    _password="${2:?Missing password}"
    _host="${3:?Missing host}"
    _port="${4:?Missing port}"
    _db="${5:-}"
    _driver="${6:-}"
    [ "${_db}" != "" ] && _db="/${_db}"
    [ "${_driver}" != "" ] && _driver="+${_driver}"
    echo "postgresql${_driver}://${_user}:${_password}@${_host}:${_port}${_db}"
}
