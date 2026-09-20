# Troubleshooting

## JSON validation prints nothing

This is expected when valid output is redirected to `/dev/null`:

```bash
sudo python3 -m json.tool \
  /etc/librenms/fortigate-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"
```

## Configuration file not found

The filename must match the value passed by LibreNMS with `-H`:

```text
/etc/librenms/fortigate-license/<HOST>.json
```

Run `check-services.php -d` to see the exact host value.

## Works as root but not as librenms

```bash
namei -l /etc/librenms/fortigate-license/192.0.2.10.json
sudo -u librenms test -r \
  /etc/librenms/fortigate-license/192.0.2.10.json \
  && echo "Configuration readable"
```

Expected ownership and modes:

```text
Directory: root:librenms 0750
File:      root:librenms 0640
```

## HTTP 401

- Confirm the token belongs to the FortiGate being queried.
- Check for accidental spaces or missing characters in `api_token`.
- Confirm the REST API administrator is enabled.
- Determine whether the token was regenerated or expired.

## HTTP 403

- Confirm Trusted Hosts includes the actual LibreNMS source IP using `/32`.
- Confirm the profile has System read access (`set sysgrp read`).
- Confirm the API administrator has access to the configured VDOM.
- Temporarily test `super_admin_readonly` only to diagnose profile permissions,
  then return to a dedicated least-privilege profile.

## TLS certificate failure

TLS verification protects the API token from interception. Choose one of the
following configurations.

### Initial deployment with certificate verification disabled

Edit the device configuration:

```bash
sudo nano /etc/librenms/fortigate-license/192.0.2.10.json
```

Set:

```json
"verify_tls": false,
"ca_file": ""
```

Validate and test:

```bash
sudo python3 -m json.tool \
  /etc/librenms/fortigate-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"

sudo -u librenms \
  /usr/lib/nagios/plugins/check_fortigate_license \
  -H 192.0.2.10 -w 60 -c 30
```

This works with self-signed certificates but does not verify the FortiGate's
identity. Use it only until trusted certificate validation is available.

### Use a private CA file for this checker

Place the issuing root CA—and any required intermediate CA certificates—in a
PEM bundle readable by `librenms`:

```bash
sudo install -d -o root -g librenms -m 0750 \
  /etc/librenms/fortigate-license/ca

sudo install -o root -g librenms -m 0644 \
  organization-fortigate-ca.pem \
  /etc/librenms/fortigate-license/ca/organization-fortigate-ca.pem
```

Then configure:

```json
"verify_tls": true,
"ca_file": "/etc/librenms/fortigate-license/ca/organization-fortigate-ca.pem"
```

### Add the CA to Ubuntu's trust store

Use a `.crt` filename containing PEM certificate data:

```bash
sudo install -o root -g root -m 0644 \
  organization-fortigate-ca.crt \
  /usr/local/share/ca-certificates/organization-fortigate-ca.crt

sudo update-ca-certificates
```

Then configure:

```json
"verify_tls": true,
"ca_file": ""
```

The checker will use Ubuntu's normal trust store.

### Certificate name mismatch

If the certificate is issued to `fortigate-mgmt.example.net`, the `host` value
must use that name, and DNS must resolve it correctly:

```json
"host": "fortigate-mgmt.example.net",
"verify_tls": true,
"ca_file": ""
```

Inspect the presented certificate:

```bash
openssl s_client \
  -connect fortigate-mgmt.example.net:443 \
  -servername fortigate-mgmt.example.net \
  -showcerts </dev/null
```

The command-line `--insecure` option is for diagnosis only. Do not add it to a
LibreNMS service template.

## Connection refused or timeout

- Confirm routing from LibreNMS to the management interface.
- Confirm TCP/443—or the configured custom port—is permitted.
- Confirm HTTPS administrative access is enabled on the target interface.
- Check the JSON `host`, `port`, `vdom`, and `timeout` values.
- Increase `timeout` only after resolving routing and policy problems.

## No parseable licence entries

The API responded but no supported licence dictionaries were parsed. Test the
endpoint directly using `docs/FORTIGATE_API_SETUP.md`. FortiOS versions can
return different structures; sanitize output before opening an issue.

## `no_license` entries appear but the service is OK

This is intentional. The checker displays all returned statuses, while the
default Critical patterns match only expired, invalid, or revoked text. Optional
services that were never purchased therefore remain visible without making the
entire firewall Critical.

## CRITICAL and exit code 2

If the output lists an expired, matched, or near-expiry entitlement, the checker
is working. Nagios exit code `2` means Critical, not a Python error.

## The Services message is blank until reload

Refresh the page after a successful service poll. Confirm the stored result:

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

Refreshing the page itself does not execute the checker.

## Unrealistic Last Changed value

**Last Changed** measures how long the stored service state has remained the
same. It is not the last poll time. An invalid/imported historical timestamp can
show an unrealistic duration. A genuine transition such as Unknown to OK should
update it. Investigate the service record and server/database time settings if
it remains incorrect.

## Duplicate service rows

A manual service and a template-created service may both exist. Identify the
service IDs first, then remove only the confirmed duplicate through the GUI.

## Services menu or check type missing

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
ls -l /usr/lib/nagios/plugins/check_fortigate_license
```

Enable Services if necessary, confirm the plugin is executable, and refresh or
sign back into the GUI.
