# Architecture

## Data flow

```text
LibreNMS service scheduler
        |
        | -H <device-host> -w 60 -c 30
        v
check_fortigate_license
        |
        | reads /etc/librenms/fortigate-license/<device-host>.json
        | HTTPS GET + Authorization: Bearer <token>
        v
FortiGate /api/v2/monitor/license/status/select/?vdom=root
        |
        | JSON licence and support-contract results
        v
Nagios exit code + one-line service message
        |
        v
LibreNMS Services database and Services dashboard
```

If the `select` endpoint returns HTTP 404, the checker tries
`/api/v2/monitor/license/status` for FortiOS compatibility.

## Components

| Component | Purpose |
|---|---|
| `plugins/check_fortigate_license` | API query, parsing, severity calculation, output |
| `/etc/librenms/fortigate-license/<HOST>.json` | Per-device host, token, TLS, VDOM, and policy settings |
| LibreNMS service/service template | Supplies the device host and threshold arguments |
| LibreNMS service scheduler | Runs checks and stores the latest result |
| FortiGate REST API administrator | Provides restricted token-based access |

## Why configuration is per device

Each FortiGate generates its own token. Per-host files prevent credentials from
appearing in LibreNMS parameters, process listings, Git, or service debug output.
They also allow different TLS certificates, ports, VDOMs, and ignored features.

## Status calculation

Each parsed item is evaluated independently. Severity is decided in this order:

1. Critical status-pattern match.
2. Expiry is at or below the Critical threshold.
3. Warning status-pattern match.
4. Expiry is at or below the Warning threshold.
5. Otherwise OK.

The overall service state is the highest severity of all items. Output is sorted
with Critical items first, then Warning, then OK.

## Security boundaries

- Tokens remain in files owned by `root:librenms` with mode `0640`.
- The configuration directory is `root:librenms` with mode `0750`.
- LibreNMS executes the checker as its unprivileged operating-system account.
- The token is sent only in the HTTPS Authorization header and is never printed.
- Trusted Hosts on the FortiGate restrict token use to the LibreNMS server.
- TLS verification should be enabled after the FortiGate certificate trust chain
  is configured.
