#!/usr/bin/env bash
set -euo pipefail

# Detect current user info
USER_UID=$(id -u)

# Clean up any old container
podman rm -f cldr-ansible 2>/dev/null || true

# Run the container
podman run -dit --pull=never \
  --name cldr-ansible \
  --hostname cldr.cloudera.dev \
  -v $(pwd):/home/$(id -un) \
  -w /home/$(id -un) \
  -v "$PWD/entreprise:/entreprise" \
  localhost/cldr-ansible:latest \
  tail -f /dev/null

