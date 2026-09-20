#!/usr/bin/env bash
set -euo pipefail

repository_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repository_root"

python3 -m py_compile plugins/check_fortigate_license
python3 -m unittest discover -s tests -p 'test_*.py'

if [[ ! -f docs/BEGINNER_DEPLOYMENT.md ]]; then
    echo "Beginner deployment guide is missing." >&2
    exit 1
fi

if [[ ! -x plugins/check_fortigate_license ]]; then
    echo "Plugin is not executable: plugins/check_fortigate_license" >&2
    exit 1
fi

if [[ ! -x scripts/install.sh || ! -x scripts/preflight.sh ]]; then
    echo "Installation helper scripts must be executable." >&2
    exit 1
fi

if grep -RInE \
    --exclude-dir=.git \
    --exclude-dir=__pycache__ \
    --exclude=check_repository.sh \
    '(KuSOC|kuwaitarmy|10\.0\.2\.|172\.29\.|172\.30\.|REPLACE_WITH_THE_DEVICE_API_TOKEN|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY)' .; then
    echo "Possible private deployment data or secret material found." >&2
    exit 1
fi

echo "Repository checks passed."
