# Security Policy

## Sensitive information

Never submit API tokens, live configuration files, internal addresses,
hostnames, serial numbers, screenshots of tokens, or unsanitized API output.

Per-device files under `/etc/librenms/fortigate-license/` must not be committed.
Use documentation addresses such as `192.0.2.0/24` in examples.

## Recommended deployment controls

- Dedicated FortiGate REST API administrator per appliance.
- Read-only profile with only the permissions required by the endpoint.
- Trusted Hosts restricted to the LibreNMS source IP using `/32`.
- Configuration directory `root:librenms` mode `0750`.
- Configuration files `root:librenms` mode `0640`.
- Verified HTTPS using the Ubuntu trust store or an explicit private CA bundle.
- Token rotation and revocation according to organizational policy.

## Reporting a vulnerability

Report security issues privately to the maintainer. Include a sanitized proof of
concept and impact description. Do not open a public issue containing secrets
or production data.
