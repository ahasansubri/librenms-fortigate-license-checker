# Beginner Deployment Guide

This guide takes a first-time administrator from an empty LibreNMS Services
setup to a working FortiGate licence check. Complete the steps in order for one
test firewall before applying a service template to a device group.

## What you need before starting

Record these values privately. The addresses below are examples only.

| Required value | Example | Where it is used |
|---|---|---|
| LibreNMS server source IP | `192.0.2.50` | FortiGate Trusted Hosts as `/32` |
| LibreNMS device host | `192.0.2.10` | Service `-H` value and JSON filename |
| FortiGate API address | `192.0.2.10` | JSON `host` value |
| FortiGate HTTPS port | `443` | JSON `port` value |
| Administrative VDOM | `root` | JSON `vdom` value |
| Dedicated API token | Keep private | JSON `api_token` value |

The **LibreNMS device host** and **FortiGate API address** are often identical,
but they do not have to be. The JSON filename must match what LibreNMS passes
with `-H`; the JSON `host` controls the actual API connection.

## Step 1 — Check the LibreNMS environment

From the extracted repository directory:

```bash
./scripts/preflight.sh
```

Confirm Services is enabled and find the configured plugin directory:

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
```

If the first command returns `false`, enable Services:

```bash
sudo -u librenms /opt/librenms/lnms config:set show_services true
```

The normal plugin directory is `/usr/lib/nagios/plugins`. Read
[Installation](INSTALLATION.md) before changing it or adding a scheduler.

## Step 2 — Create the FortiGate API administrator

On the FortiGate, open **System > Administrators > Create New > REST API Admin**.

Use:

| Field | Value |
|---|---|
| Username | `librenms-api` |
| Comments | `LibreNMS FortiGate licence monitoring` |
| Administrator profile | Read-only profile with **System = Read** |
| PKI Group | Off |
| CORS Allow Origin | Off |
| Restrict login to trusted hosts | On |
| Trusted Host | LibreNMS source IP with `/32` |

Save the generated token securely. FortiGate normally shows it only at creation
time. Create a different token on every firewall; do not use `super_admin` for
ongoing monitoring.

See [FortiGate API setup](FORTIGATE_API_SETUP.md) for permission tests and HTTP
401/403 troubleshooting.

## Step 3 — Install the checker

From the repository root:

```bash
sudo ./scripts/install.sh
```

Confirm the installation:

```bash
ls -l /usr/lib/nagios/plugins/check_fortigate_license
sudo -u librenms test -x \
  /usr/lib/nagios/plugins/check_fortigate_license \
  && echo "Checker executable by librenms"
```

LibreNMS removes `check_` from the filename, so the check type becomes:

```text
fortigate_license
```

## Step 4 — Create the protected device configuration

Use the exact LibreNMS device host as the filename. For example:

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/fortigate-license/192.0.2.10.json

sudo nano /etc/librenms/fortigate-license/192.0.2.10.json
```

Set the real management address and token:

```json
{
  "host": "192.0.2.10",
  "port": 443,
  "api_token": "PASTE_THE_RESTRICTED_API_TOKEN_HERE",
  "vdom": "root",
  "verify_tls": false,
  "ca_file": "",
  "timeout": 20,
  "ignore_features": [],
  "critical_status_patterns": ["*expired*", "*invalid*", "*revoked*"],
  "warning_status_patterns": ["*warning*", "*expiring*"]
}
```

`verify_tls: false` works with an initial self-signed certificate but does not
authenticate the firewall. Move to verified TLS using the Ubuntu trust store or
a private CA file after initial testing. See
[TLS certificate failure](TROUBLESHOOTING.md#tls-certificate-failure).

Validate syntax, ownership, and readability:

```bash
sudo python3 -m json.tool \
  /etc/librenms/fortigate-license/192.0.2.10.json >/dev/null \
  && echo "JSON syntax valid"

sudo chown root:librenms \
  /etc/librenms/fortigate-license/192.0.2.10.json
sudo chmod 0640 \
  /etc/librenms/fortigate-license/192.0.2.10.json

sudo -u librenms test -r \
  /etc/librenms/fortigate-license/192.0.2.10.json \
  && echo "Configuration readable"
```

## Step 5 — Test outside the LibreNMS GUI

Run the installed checker as the same account LibreNMS uses:

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_fortigate_license \
  -H 192.0.2.10 \
  -w 60 -c 30

echo "Exit code: $?"
```

The checker automatically reads:

```text
/etc/librenms/fortigate-license/192.0.2.10.json
```

Interpret the result:

| Exit code | Meaning |
|---:|---|
| `0` | Check succeeded; evaluated licences are OK |
| `1` | Check succeeded; at least one item is Warning |
| `2` | Check succeeded; at least one item is Critical |
| `3` | Monitoring failed; investigate configuration/API/TLS/connectivity |

Warning or Critical output is not a Python failure. It means the API query and
parsing worked and found a condition matching the configured policy.

## Step 6 — Create the LibreNMS service template

Create and review a FortiGate device group first. Then open:

**Services > Service Templates > Add Service Template**

| Field | Value |
|---|---|
| Name | `FortiGate Licence Status` |
| Device Type | `Static` |
| Select Devices | Leave empty |
| Device Groups | Your reviewed FortiGate group |
| Check Type | `fortigate_license` |
| Description | `FortiGate Licence and Support Status` |
| Remote Host | Leave empty |
| Parameters | `-w 60 -c 30` |

Do not add `--config`. The service host selects the matching JSON file
automatically.

If this is dashboard-only monitoring, turn the template's **Alert** option off
when available. Do not create a licence service alert rule, and verify that no
generic rule alerts on every non-zero service status.

## Step 7 — Poll and verify

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

The request should contain:

```text
'check_fortigate_license' '-H' '192.0.2.10' '-w' '60' '-c' '30'
```

Then open **Services > All Services**. A healthy integration shows:

- check type `fortigate_license`;
- a green, yellow, red, or Unknown state matching the exit code;
- licence and support-contract details in the Message column;
- no missing-configuration or permission error.

LibreNMS **Last Changed** is the age of the current service state—not the last
poll time and not the licence expiry age.

## Step 8 — Add more FortiGates

For every additional appliance:

1. Create a dedicated REST API administrator and token.
2. Create `/etc/librenms/fortigate-license/<LIBRENMS-HOST>.json`.
3. Test it as `librenms` before adding it to the device group.
4. Let the single service template create the service.

For HA, monitor each physical member using its own management address, token,
JSON file, and LibreNMS service. See [Multiple FortiGates and HA](MULTIPLE_FIREWALLS.md).

## Quick troubleshooting order

When a service is Unknown, check in this order:

1. Does the JSON filename exactly match the service `-H` value?
2. Can `librenms` read the file?
3. Does the token belong to this firewall?
4. Does Trusted Hosts contain the actual source IP?
5. Does the API profile have System read access?
6. Can LibreNMS reach the configured HTTPS port?
7. Is TLS verification configured for the presented certificate?

Continue with the complete [Troubleshooting guide](TROUBLESHOOTING.md).
