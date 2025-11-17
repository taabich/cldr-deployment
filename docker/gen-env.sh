# gen-env.sh
#!/usr/bin/env bash
set -euo pipefail
USER_UID="$(id -u)"
USER_GID="$(id -g)"
if [ "$USER_GID" -lt 1000 ]; then USER_GID=1000; fi
USERNAME="$(id -un)"

cat > .env <<EOF
USERNAME=${USERNAME}
USER_UID=${USER_UID}
USER_GID=${USER_GID}
EOF

echo "Generated .env:"
cat .env