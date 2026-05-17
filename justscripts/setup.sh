#!/usr/bin/env sh
. justscripts/shell.sh

setup_repo_name(){
    if check_if_name_set;then
        echo_warning "Name already set."
        return 1
    fi
    read -rp "Pass project name:" name
    if ! is_valid_filename ${name} || ! is_valid_python_package_name ${name}; then
        echo_warning "Name ${name} is not a valid repo name."
        return 1
    fi
    echo_default "Replacing the package name placeholder with the repo name..."
    mv src/project_name src/${name}
    echo_default "Replacing placeholder with the repo name in files..."
    find . -type f ! -name "setup.sh" -exec sed -i "s/<project_name>/$name/g" {} +
}

check_if_name_set(){
    flag=${1}
    name_set=0
    if grep -qR "<project_name>" --exclude="setup.sh" . ;then
        [ "${flag}" = "verbose" ] && echo_warning "Project name not set."
        name_set=1
    fi
    if [ -d "src/package_name" ];then
        [ "${flag}" = "verbose" ] && echo_warning "project_name/ directory exists."
        name_set=1
    fi
    return ${name_set}
}