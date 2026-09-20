#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
    echo "Run this installer as root: sudo ./scripts/install.sh" >&2
    exit 1
fi

repository_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
plugin_directory=${NAGIOS_PLUGIN_DIR:-/usr/lib/nagios/plugins}

if ! getent group librenms >/dev/null; then
    echo "The librenms group does not exist. Install LibreNMS first." >&2
    exit 1
fi

install -d -o root -g root -m 0755 "$plugin_directory"
install -o root -g root -m 0755 \
    "$repository_root/plugins/check_fortigate_license" \
    "$plugin_directory/check_fortigate_license"

install -d -o root -g librenms -m 0750 \
    /etc/librenms/fortigate-license

echo "Installed: $plugin_directory/check_fortigate_license"
echo "Created:   /etc/librenms/fortigate-license"
echo "Next: follow docs/FORTIGATE_API_SETUP.md and docs/INSTALLATION.md"
