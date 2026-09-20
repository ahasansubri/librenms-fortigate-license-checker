# FortiGate Licence Checker for LibreNMS

A dependency-free Python plugin that reads FortiGate licence and support-contract
information through the FortiOS REST API and displays it in the LibreNMS
**Services** page.

The LibreNMS check type is:

```text
fortigate_license
```

## What it does

For each FortiGate, LibreNMS runs the checker on the normal Services polling
schedule. The checker:

1. Loads that firewall's protected API token file.
2. Queries the FortiOS licence monitor endpoint over HTTPS.
3. Reads flat licence entries and nested support contracts.
4. Calculates the days remaining for entries that include an expiry date.
5. Returns an OK, Warning, Critical, or Unknown Nagios-compatible result.
6. Shows every returned licence status and expiry date in **Services > All Services**.

It does **not** use SNMP, SNMP traps, a LibreNMS database password, or an agent
installed on the firewall.

## Status logic

| Exit code | LibreNMS state | Default meaning |
|---:|---|---|
| `0` | OK | No evaluated item matched a warning/critical rule |
| `1` | Warning | An expiry is 31–60 days away, or a warning status pattern matched |
| `2` | Critical | An expiry is 30 days or fewer away, or an expired/invalid/revoked pattern matched |
| `3` | Unknown | Configuration, API, TLS, connectivity, or parsing failed |

Statuses such as `no_license` are still displayed but are not Critical by
default. This avoids treating intentionally unpurchased FortiGuard services as
failures. You can change the status patterns in each device configuration.

An exit code of `2` is not a script failure when an entitlement is expired. It
means the checker worked and detected a Critical condition.

## Requirements

- LibreNMS with Services enabled
- Python 3.10 or newer
- HTTPS connectivity from LibreNMS to each FortiGate management interface
- A dedicated FortiGate REST API administrator with read-only System access
- One API token and protected JSON configuration per physical FortiGate

The plugin uses only the Python standard library.

## Beginner quick start

For a single end-to-end walkthrough with expected results, start with the
[Beginner Deployment Guide](docs/BEGINNER_DEPLOYMENT.md). The shorter summary
below is useful after you understand the workflow.

### 1. Create the FortiGate API administrator

On the FortiGate, open **System > Administrators**, create a **REST API Admin**
named `librenms-api`, assign a read-only profile with **System = Read**, and
restrict Trusted Hosts to the LibreNMS server address using `/32`.

Full instructions: [FortiGate API setup](docs/FORTIGATE_API_SETUP.md).

### 2. Install the checker

```bash
git clone https://github.com/YOUR-USERNAME/librenms-fortigate-license-checker.git
cd librenms-fortigate-license-checker
sudo ./scripts/install.sh
```

### 3. Create one protected configuration

The example below uses the documentation address `192.0.2.10`. Replace it with
the address LibreNMS passes to the service as `-H`.

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/fortigate-license/192.0.2.10.json

sudo nano /etc/librenms/fortigate-license/192.0.2.10.json
```

Set the real host and API token. Never commit that file to Git.

### 4. Test as the LibreNMS user

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_fortigate_license \
  -H 192.0.2.10 \
  -w 60 -c 30

echo "Exit code: $?"
```

Because the filename matches the host, `--config` is optional. The checker
automatically opens:

```text
/etc/librenms/fortigate-license/<HOST>.json
```

### 5. Create the LibreNMS service template

Open **Services > Service Templates > Add Service Template**:

| Field | Value |
|---|---|
| Name | `FortiGate Licence Status` |
| Device Type | `Static` |
| Select Devices | Leave empty |
| Device Groups | Your FortiGate device group |
| Check Type | `fortigate_license` |
| Description | `FortiGate Licence and Support Status` |
| Remote Host | Leave empty |
| Parameters | `-w 60 -c 30` |

Do not add `--config` to the template. Automatic per-host configuration lets
one template cover every FortiGate in the group.

## Important HA rule

Monitor both physical members of an HA pair. Each member has its own management
address, API token, serial number, subscriptions, and configuration file.

## Documentation

- [Beginner deployment guide](docs/BEGINNER_DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)
- [FortiGate API setup](docs/FORTIGATE_API_SETUP.md)
- [Installation and environment setup](docs/INSTALLATION.md)
- [LibreNMS service setup](docs/LIBRENMS_SETUP.md)
- [Multiple FortiGates and HA](docs/MULTIPLE_FIREWALLS.md)
- [Operations](docs/OPERATIONS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Security policy](SECURITY.md)

Official background documentation:

- [LibreNMS Nagios Plugins and Services](https://docs.librenms.org/Extensions/Services/)
- [Fortinet: REST API administrator](https://docs.fortinet.com/document/fortigate/7.4.8/administration-guide/399023/rest-api-administrator)
- [Fortinet FortiOS monitor facts (`license_status` selector)](https://docs.ansible.com/projects/ansible/latest/collections/fortinet/fortios/fortios_monitor_fact_module.html)

## Privacy and output safety

The checker never prints the API token. It displays licence names, status text,
expiry dates, and calculated remaining days. Sanitize API responses before
sharing them because FortiOS responses can include a device serial number.

## Maintainer

Ahasan Subri

## Licence

No licence file is included. Public visibility alone does not grant permission
to copy, modify, or redistribute this project. Add an explicit open-source
licence later only if the maintainer chooses to grant those rights.
