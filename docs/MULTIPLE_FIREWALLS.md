# Multiple FortiGates and HA

## One JSON file per device host

The filename must exactly match the value LibreNMS passes with `-H`:

```text
/etc/librenms/fortigate-license/192.0.2.10.json
/etc/librenms/fortigate-license/192.0.2.11.json
/etc/librenms/fortigate-license/branch-fw.example.net.json
```

Use this command to see the actual host value:

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

If the LibreNMS hostname is an IP address, use that IP as the filename. If it is
an FQDN, use the FQDN unless an explicit `--config` parameter is supplied.

## One service template for the fleet

Assign a single template to a validated FortiGate device group. Leave Remote
Host empty and use only:

```text
-w 60 -c 30
```

As devices join the group, the template can create their service. The service
will return Unknown until its protected JSON file exists.

## HA pairs

Create a separate API administrator, token, JSON file, and LibreNMS service for
each physical member. Do not assume an HA virtual address provides complete
visibility of both members' entitlements.

Example documentation layout:

| Physical member | LibreNMS host | Configuration |
|---|---|---|
| Primary member | `192.0.2.10` | `192.0.2.10.json` |
| Secondary member | `192.0.2.11` | `192.0.2.11.json` |

## Non-standard API address

The filename follows LibreNMS, but the `host` property controls the actual API
destination. This is useful when LibreNMS identifies the device by FQDN while
the API must use a dedicated management address.

```json
{
  "host": "fortigate-mgmt.example.net",
  "port": 8443
}
```

Keep all other required configuration properties in the file.

## Different VDOMs

Set `vdom` per configuration. Licence status is generally obtained from the
management/global context, but permissions and behavior can differ by FortiOS
version and administrative domain. An HTTP 403 should be investigated as a
profile/VDOM scope issue before broadening access permanently.
