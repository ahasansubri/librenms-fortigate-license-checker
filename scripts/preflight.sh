#!/usr/bin/env bash
set -u

failures=0

check_command() {
    local command_name=$1
    if command -v "$command_name" >/dev/null 2>&1; then
        printf '[OK]   Command available: %s\n' "$command_name"
    else
        printf '[FAIL] Command missing: %s\n' "$command_name"
        failures=$((failures + 1))
    fi
}

check_path() {
    local path=$1
    local description=$2
    if [[ -e "$path" ]]; then
        printf '[OK]   %s: %s\n' "$description" "$path"
    else
        printf '[FAIL] %s missing: %s\n' "$description" "$path"
        failures=$((failures + 1))
    fi
}

check_command python3
check_command curl
check_command sudo

if id librenms >/dev/null 2>&1; then
    echo '[OK]   LibreNMS operating-system account exists'
else
    echo '[FAIL] LibreNMS operating-system account is missing'
    failures=$((failures + 1))
fi

check_path /opt/librenms/lnms 'LibreNMS CLI'
check_path /opt/librenms/check-services.php 'LibreNMS service checker'
check_path /opt/librenms/services-wrapper.py 'LibreNMS service wrapper'

if dpkg-query -W -f='${Status}\n' monitoring-plugins 2>/dev/null |
    grep -qx 'install ok installed'; then
    echo '[OK]   monitoring-plugins package is installed'
else
    echo '[WARN] monitoring-plugins package was not detected'
fi

if [[ -x /usr/lib/nagios/plugins/check_fortigate_license ]]; then
    echo '[OK]   FortiGate checker is installed and executable'
else
    echo '[WARN] FortiGate checker is not installed yet'
fi

echo
if (( failures > 0 )); then
    printf 'Preflight completed with %d required failure(s).\n' "$failures"
    exit 1
fi

echo 'Preflight completed without required failures.'
