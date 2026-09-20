# LibreNMS Service Setup

## 1. Confirm the check type appears

The installed executable is:

```text
/usr/lib/nagios/plugins/check_fortigate_license
```

LibreNMS derives the check type by removing `check_`:

```text
fortigate_license
```

If it does not appear, verify the configured plugin directory and permissions:

```bash
sudo -u librenms /opt/librenms/lnms config:get nagios_plugins
ls -l /usr/lib/nagios/plugins/check_fortigate_license
```

## 2. Create or select a FortiGate device group

A dynamic group is recommended. In LibreNMS, create a device group whose rule
matches FortiGate devices, commonly by using the detected OS value `fortigate`.
Review the group's members before applying the service template.

## 3. Create the service template

Open **Services > Service Templates > Add Service Template**:

| Field | Value |
|---|---|
| Name | `FortiGate Licence Status` |
| Device Type | `Static` |
| Select Devices | Leave empty |
| Device Groups | Your FortiGate group |
| Check Type | `fortigate_license` |
| Description | `FortiGate Licence and Support Status` |
| Remote Host | Leave empty |
| Parameters | `-w 60 -c 30` |

Do **not** put `--config` in Parameters. LibreNMS supplies `-H <device-host>`,
and the checker automatically opens:

```text
/etc/librenms/fortigate-license/<device-host>.json
```

Create the matching JSON file before adding each firewall to the device group.

## 4. Prevent email alerts when using dashboard-only monitoring

- Turn the service/template **Alert** option off when the GUI provides it.
- Do not create a licence service alert rule.
- Check that an existing generic service rule does not match all non-zero
  `services.service_status` values.

The service can still be green, yellow, red, or Unknown in the Services page
without sending an email.

## 5. Poll immediately

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

The debug request should look similar to:

```text
'/usr/lib/nagios/plugins/check_fortigate_license' '-H' '192.0.2.10' '-w' '60' '-c' '30'
```

Open **Services > All Services** and confirm that the Message column shows the
licence and support-contract statuses.

## 6. Optional database verification

```sql
SELECT service_id,
       device_id,
       service_type,
       service_ip,
       service_status,
       service_message
FROM services
WHERE service_type = 'fortigate_license';
```

Status values are `0` OK, `1` Warning, `2` Critical, and `3` Unknown.

## What “Last Changed” means

LibreNMS **Last Changed** is the time since the stored service state last
changed—for example, OK to Warning. It is not the last polling time and not the
licence expiry age. If imported service data has an invalid historical timestamp,
the GUI can initially show an unrealistic duration; a real state change normally
resets it.
