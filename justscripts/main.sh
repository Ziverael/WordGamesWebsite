#!/usr/bin/env sh
# shellcheck disable=SC2015
# shellcheck disable=SC2120
. justscripts/env.sh
. justscripts/setup.sh
. justscripts/shell.sh

init_project(){
    check_if_name_set "verbose"
    create_default_directories_and_files
    init_local_venv
    create_or_update_dotenv
}

refresh_project(){
    sync_local_venv
    create_or_update_dotenv
}

format_code () {
    TARGET="${1:-./}"
    IGNORE="${2}"
    [ -f "${TARGET}" ] && [ "$(get_lowercase_file_extension "${TARGET}")" != "py" ]\
        && echo "Not a python file. Skipped." && return
    [ -n "${IGNORE}" ] && IGNORE="--ignore ${IGNORE}"
    echo_title "Starting reformat with ruff..."
    uv run ruff format "${TARGET}" || ERROR=$?
    # shellcheck disable=SC2086
    uv run ruff check --fix ${IGNORE} "${TARGET}" || ERROR=$?
    show_ruff_hints_if_error_encountered ${ERROR}
}

check_code () {
    echo_title "Starting check with ruff..."
    uv run ruff check . || ERROR=$?
    uv run ruff format --check . || ERROR=$?
    show_ruff_hints_if_error_encountered ${ERROR}
    echo_title "Starting check with mypy..."
    uv run mypy --incremental --show-error-codes --pretty . || ERROR=$?
    return $ERROR
}

show_ruff_hints_if_error_encountered () {
    ERROR="${1}"
    if [ -n "${ERROR}" ]
    then
        echo_default "Rule details available at https://docs.astral.sh/ruff/rules/."
    fi
}

test_code () {
    TEST_PATH="${1:-./tests}"
    echo_title "Starting tests with pytest..."
    OPTS="${3}"
    OPTS="${OPTS} --cov ."
    OPTS="${OPTS} --cov-report html:.local/coverage/htmlcov"
    OPTS="${OPTS} --cov-report xml:.local/coverage/coverage.xml"
    OPTS="${OPTS} --cache-clear"
    OPTS="${OPTS} --pyargs ${TEST_PATH}"
    uv  run pytest ${OPTS}
    echo "Coverage report available at $(pwd).local/coverage/htmlcov/index.html."
}

clean_pycached () {
    echo_title "Removing all __pycache__ directories and *.py[cod] files..."
    find . -type f -name "*.py[cod]" -delete -or -type d -name "__pycached__" -delete
    echo_default "Done"
}

open_coverage_report () {
    echo_title "Opening coverage report..."
    if [ -f ".local/coverage/htmlcov/index.html" ]
    then
        open_in_browser ".local/coverage/htmlcov/index.html"
    else
        echo_error "Coverage report not found..."
    fi
}

profile_python_code () {
    FILE="${1:?}"
    echo_title "Profiling with scalene..."
    uv run scalene run ${FILE} --html --outfile ".local/scalene/$(basename "${FILE%.*}").html"
    echo_title "Opening scalene report in default browser..."
    open_in_browser ".local/${PROJECT_NAME}/scalene/$(basename "${FILE%.*}").html"
}

init_local_venv(){
    echo_title "Initializing local venv..."
    uv sync
    echo_default "Initializing pre-commit..."
    uv run --no-sync pre-commit install
}

sync_local_venv(){
    echo_title "Synchronizing local venv..."
    uv sync
}

create_default_directories_and_files(){
    TMP_FILE=$(mktemp)
    {
        create_directory_if_it_does_not_exist ".local"
        create_directory_if_it_does_not_exist "tmp"
        create_directory_if_it_does_not_exist "data"
        create_directory_if_it_does_not_exist "scalene"
    } >> "${TMP_FILE}"
    if [ -n "$(cat "${TMP_FILE}")" ]
    then
        echo_title "Creating files and directories..."
        echo_default "$(grep -v '^$' "${TMP_FILE}")"
    fi
    rm -f "${TMP_FILE}"
}
