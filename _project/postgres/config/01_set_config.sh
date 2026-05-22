#!/bin/bash
set -e

config_files_directory="/etc/postgresql"

if [ -d "${config_files_directory}" ]
then
  echo "creating config files"
  ls ${config_files_directory}
  cp ${config_files_directory}/* /var/lib/postgresql/data
fi
