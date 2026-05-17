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
    else
        echo_title "Updating .env file..."
        rm -f .local/.env.backup && cp .env .local/.env.backup && rm -f .env && cp .env.template .env
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
