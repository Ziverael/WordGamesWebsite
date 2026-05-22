#!/usr/bin/env sh

podman_network_exists(){
  _network="${1:?}"
  [ "$(podman network ls | grep -w "${_network}")" != "" ] && echo "true" || echo "false"
}

podman_image_exists(){
  _image_name="${1:?}"
  [ "$(podman images --quiet "${_image_name}")" != "" ] && echo "true" || echo "false"
}

podman_container_is_running(){
  _temporary_container="${1:?}"
  [ "$(podman inspect -f '{{.State.Running}}' "${_temporary_container}" 2> /dev/null)" = "true" ] && echo "true" || echo "false"
}

conflicting_podman_container_exists(){
  _temporary_container="${1:?}"
  _current_project="${COMPOSE_PROJECT_NAME:-$(basename "$(pwd)")}"
  _containers_exists="$([ -n "$(podman ps --quiet --all --filter name="^${_temporary_container}$")" ] && echo "true" || echo "false")"
  _container_project="$(podman inspect -f '{{index .Config.Labels "com.podman.compose.project"}}' "${_temporary_container}" 2> /dev/null)"
  [ "${_containers_exists}" = "true" ] && [ "${_container_project}" != "${_current_project}" ] && echo "true" || echo "false"
}

conflicting_podman_container_is_running(){
  _temporary_container="${1:?}"
  [ "$(podman_container_is_running "${_temporary_container}")" = "true" ] && [ "$(conflicting_podman_container_exists "${_temporary_container}")" = "true" ] && echo "true" || echo "false"
}

conflicting_podman_container_is_stopped(){
  _temporary_container="${1:?}"
  [ "$(podman_container_is_running "${_temporary_container}")" = "false" ] && [ "$(conflicting_podman_container_exists "${_temporary_container}")" = "true" ] && echo "true" || echo "false"
}

create_shared_network(){
  _network="${1:?}"
	if [ "$(podman_network_exists "${_network}")" != "true" ]
	then
		echo_title "Creating network ${_network}"
		podman network create "${_network}"
	fi
}

validate_if_image_exists(){
  _image="${1:?}"
  if [ "$(podman_image_exists "${_image}")" != "true" ]
  then
      echo_title "Checking if image ${_image} exists"
      echo_warning "Image ${HIGHLIGHT}${_image}${WARNING} is missing." 1>&2
      return 1
  fi
}

start_service_if_it_is_not_running(){
  _service="${1:?}"
  _compose_file="${2:?}"
  if [ "$(podman_container_is_running "${_service}")" != "true" ]
  then
    echo_title "Starting ${_service} service"
    podman-compose -f "${_compose_file}" up -d "${_service}"
	fi
}

stop_service_if_it_is_running(){
  _compose_file="${1:?}"
  _service="${2:?}"
  if [ "$(podman_container_is_running "${_service}")" = "true" ]
  then
    echo_title "Stopping ${_service} service"
    podman-compose -f "${_compose_file}" down "${_service}"
	fi
}
