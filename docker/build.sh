#!/usr/bin/env bash
set -euo pipefail

# Detect current user info
USER_UID=$(id -u)
USER_GID=$(id -g)


if [ "$USER_GID" -lt 1000 ]; then
  USER_GID=1000
fi


podman build \
  --build-arg USERNAME=$(id -un) \
  --build-arg USER_UID=$(id -u) \
  --build-arg USER_GID=$USER_GID \
  -t cldr-deploy docker