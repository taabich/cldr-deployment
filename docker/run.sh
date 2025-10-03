#!/usr/bin/env bash
set -euo pipefail

# Detect current user info
UID_CUR=$(id -u)
GID_CUR=$(id -g)
HOME_CUR=/home/$USER

if [ "$GID_CUR" -lt 1000 ]; then
  GID_CUR=1000
fi

# Clean up any old container
podman rm -f cldr-ansible 2>/dev/null || true

# Run the container
podman run -dit --pull=never \
  --name cldr-ansible \
  --hostname cldr.cloudera.dev \
  --workdir ${HOME_CUR} \
  -v "$PWD/:/projects" \
  -v "$PWD/entreprise:/entreprise" \
  localhost/cldr-ansible:latest \
  tail -f /dev/null

