@default:
    just help

help:
    #!/usr/bin/env sh
    {{sh_init}}
    echo_title "General recipes:"
    echo_default "help                 Show this message."
    echo_default "setup_repo_name      Set project name. Run at the beginning."
    echo_default "init                 Initialize the project. Run after \`set_name\`."
    echo_default "refresh              Refresh the project with its pyproject.toml."
    echo_default "update_dotenv        Recreate the .env file from the .env.template file."
    echo_default "format               Format <project_name> code with ruff. Example usage:"
    echo_highlight "                         just format"
    echo_default "                       format specific file:"
    echo_highlight "                         just format <FilePathRelativeToProjectRoot>"
    echo_default "check                Verify the application code compliance against ruff, and mypy checks."
    echo_default "test                 Run the test suite. Example usage:"
    echo_default "all                  format + check + test."
    echo_default "                       run all tests:"
    echo_highlight "                         just test"
    echo_default "                       run specific test or tests:"
    echo_highlight "                         just test ./tests"
    echo_highlight "                         just test ./tests/test_something.py"
    echo_highlight "                         just test ./tests/test_something.py::test_it"
    echo_title "Other recipes:"
    echo_default "clean_pycached       Remove .py[cod] files with __pycached__ dirs."
    echo_default "coverage_report      Open coverage report with default browser."

setup_repo_name:
    #!/usr/bin/env sh
    {{sh_init}}
    setup_repo_name

init:
    #!/usr/bin/env sh
    {{sh_init}}
    init_project

refresh:
    #!/usr/bin/env sh
    {{sh_init}}
    refresh_project

update_dotenv:
    #!/usr/bin/env sh
    {{sh_init}}
    create_or_update_dotenv

default_target := './'
default_ignore := ''
format target=default_target ignore=default_ignore:
    #!/usr/bin/env sh
    {{sh_init}}
    format_code {{target}} {{ignore}}

check:
    #!/usr/bin/env sh
    {{sh_init}}
    check_code

default_test_path := './tests'
default_opts        := ''
test test_path=default_test_path opts=default_opts:
    #!/usr/bin/env sh
    {{sh_init}}
    test_code {{test_path}} {{opts}}

format_and_check: format check
all: format check test

clean_pycached:
    #!/usr/bin/env sh
    {{sh_init}}
    clean_pycached

coverage_report:
    #!/usr/bin/env sh
    {{sh_init}}
    open_coverage_report

profile file:
    #!/usr/bin/env sh
    {{sh_init}}
    profile_python_code {{file}}

# Just global variables

set dotenv-load

alias a     := all
alias c     := check
alias cr    := coverage_report
alias f     := format
alias fc    := format_and_check
alias t     := test
alias ud    := update_dotenv



TITLE       := '\033[94m\033[1m'
HIGHLIGHT   := '\033[93m\033[1m'
WARNING     := '\033[91m\033[1m'
DEFAULT     := '\033[0m'

sh_init := "set -e && PROJECT_DIR=$(pwd) && . $PROJECT_DIR/justscripts/main.sh"