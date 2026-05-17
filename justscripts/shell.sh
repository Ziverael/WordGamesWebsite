#!/usr/bin/env sh

# Shell helpers
TITLE="\033[94m\033[1m"
HIGHLIGHT="\033[93m\033[1m"
WARNING="\033[91m\033[1m"
DEFAULT="\033[0m"

echo_default(){
  echo "${DEFAULT}${1}"
}

echo_title(){
  echo "${TITLE}${1}${DEFAULT}"
}

echo_highlight(){
  echo "${HIGHLIGHT}${1}${DEFAULT}"
}

echo_warning(){
  echo "${WARNING}${1}${DEFAULT}"
}

is_arm_architecture(){
  { [ "$(uname -p)" = "arm" ] || [ "${IS_ARM_ARCHITECTURE}" = "true" ]; } && echo true || echo "false"
}

sed_inplace(){
  if [ "$(is_arm_architecture)" = "true" ]
  then
    # MacOS invocation
    sed -i '' "$@"
  else
    # Linux invocation
    sed -i "$@"
  fi
}

get_lowercase_file_extension(){
  FILENAME="${1:?}"
  LOWERCASE_FILENAME="$(echo "${FILENAME}" | tr '[:upper:]' '[:lower:]')"
  LOWERCASE_EXTENSION="${LOWERCASE_FILENAME##*.}"
  [ "${LOWERCASE_FILENAME}" != "${LOWERCASE_EXTENSION}" ] && echo "${LOWERCASE_EXTENSION}"
}

create_directory_if_it_does_not_exist(){
    DIRECTORY="${1:?}"
    [ ! -d "${DIRECTORY}" ] && mkdir -p "${DIRECTORY}" && echo "Directory ${DIRECTORY} created." || echo
}

create_file_if_it_does_not_exist(){
    FILENAME="${1:?}"
    [ -d "${FILENAME}" ] && rm -rdf "${FILENAME}" && echo "Removing directory ${FILENAME}."
    [ ! -f "${FILENAME}" ] && touch "${FILENAME}" && echo "File ${FILENAME} created." || echo
}

open_in_browser(){
  FILE="${1:?}"
  if [ -f "${FILE}" ]
  then
    nohup xdg-open "${FILE}" > /dev/null 2>&1 &
  fi
}

is_valid_filename(){
  name=${1}
  [ -n "${name}" ] || return 1
  [ "${name}" != "." ] || return 1
  [ "${name}" != ".." ] || return 1
  case "${name}" in
    */*) return 1;;
  esac
  case "${name}" in
    *[!A-Za-z0-9._-]* ) return 1;;
    esac
}

is_valid_python_package_name(){
  name=${1}
  [ -n "$name" ] || return 1
  case "$name" in
    [0-9]* ) return 1 ;;
  esac
  case "$name" in
    *[!A-Za-z0-9_]* ) return 1 ;;
  esac
  case "$name" in
    [A-Za-z_]* ) : ;;
    * ) return 1 ;;
  esac
  case "$name" in
    False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)
      return 1
      ;;
  esac
  return 0
}
