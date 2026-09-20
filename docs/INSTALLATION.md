# Installation and Environment Setup

These steps assume LibreNMS is installed under `/opt/librenms` on Ubuntu.

## 1. Run the preflight check

```bash
./scripts/preflight.sh
```

It checks Python, curl, sudo, the `librenms` account, and the LibreNMS service
polling files. Warnings about this checker are expected before installation.

## 2. Enable LibreNMS Services

Check the current setting:

```bash
sudo -u librenms /opt/librenms/lnms config:get show_services
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
```

If Services is disabled:

```bash
sudo -u librenms /opt/librenms/lnms config:set show_services true
```

The plugin directory should normally be:

```text
/usr/lib/nagios/plugins
```

Install the standard plugin package if your LibreNMS Services environment does
not already have it:

```bash
sudo apt update
sudo apt install monitoring-plugins
```

This custom checker itself uses only Python's standard library.

## 3. Confirm service scheduling

LibreNMS must periodically run `services-wrapper.py`. Check the installation's
scheduler before adding another cron entry:

```bash
sudo grep -R "services-wrapper.py" \
  /etc/cron.d /etc/systemd/system /lib/systemd/system 2>/dev/null
```

Configure exactly one supported service-polling method. Duplicate schedulers
can run every check twice.

## 4. Install the checker

From the repository root:

```bash
sudo ./scripts/install.sh
```

This installs:

```text
/usr/lib/nagios/plugins/check_fortigate_license
/etc/librenms/fortigate-license/
```

Manual equivalent:

```bash
sudo install -o root -g root -m 0755 \
  plugins/check_fortigate_license \
  /usr/lib/nagios/plugins/check_fortigate_license

sudo install -d -o root -g librenms -m 0750 \
  /etc/librenms/fortigate-license
```

The filename creates the LibreNMS check type `fortigate_license`.

## 5. Create one configuration per FortiGate

```bash
sudo install -o root -g librenms -m 0640 \
  examples/config.json.example \
  /etc/librenms/fortigate-license/192.0.2.10.json

sudo nano /etc/librenms/fortigate-license/192.0.2.10.json
```

Example:

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

`verify_tls: false` is useful for an initial deployment with a self-signed
certificate, but it disables certificate validation. See the TLS section in
[Troubleshooting](TROUBLESHOOTING.md#tls-certificate-failure) for production
options.

Validate and protect the file:

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

## 6. Test the installed checker

```bash
sudo -u librenms \
  /usr/lib/nagios/plugins/check_fortigate_license \
  -H 192.0.2.10 \
  --config /etc/librenms/fortigate-license/192.0.2.10.json \
  -w 60 -c 30

echo "Exit code: $?"
```

After this succeeds, configure LibreNMS using [LibreNMS setup](LIBRENMS_SETUP.md).
