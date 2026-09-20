# FortiGate API Setup

Create a separate API administrator on every FortiGate. Do not reuse a human
administrator or share one token between appliances.

## 1. Confirm or create a read-only profile

In the FortiGate GUI, open **System > Admin Profiles**. Use a read-only profile
that has at least:

```text
System: Read
```

You can inspect an existing profile from the CLI:

```text
show full-configuration system accprofile read-only
```

Confirm it contains:

```text
set sysgrp read
```

Start with this least-privilege profile. If the licence endpoint returns HTTP
403, temporarily test `super_admin_readonly` only to confirm that permissions
are the cause. Do not use `super_admin` for ongoing monitoring.

## 2. Create the REST API administrator

Open **System > Administrators > Create New > REST API Admin** and use:

| Field | Value |
|---|---|
| Username | `librenms-api` |
| Comments | `LibreNMS FortiGate licence monitoring` |
| Administrator profile | Read-only profile with System read access |
| PKI Group | Off |
| CORS Allow Origin | Off |
| Restrict login to trusted hosts | On |
| Trusted Hosts | LibreNMS server IP with `/32` |

Example documentation address:

```text
192.0.2.50/32
```

Use the real LibreNMS source address seen by the FortiGate. If routing performs
SNAT, configure the translated source address.

## 3. Save the token securely

FortiGate displays the API token when it is generated. Copy it directly to a
password manager or the protected configuration on the LibreNMS server.

Do not put the token in:

- shell history;
- LibreNMS service parameters;
- screenshots or tickets;
- source code or Git commits;
- email or chat messages.

Each FortiGate generates a different token.

## 4. Test the endpoint from LibreNMS

Avoid typing the token directly into the command line. Read it silently into a
temporary shell variable:

```bash
read -rsp "FortiGate API token: " FORTIGATE_TOKEN
echo

curl -ksS \
  -H "Authorization: Bearer ${FORTIGATE_TOKEN}" \
  -H "Accept: application/json" \
  "https://192.0.2.10/api/v2/monitor/license/status/select/?vdom=root" \
  | python3 -m json.tool

unset FORTIGATE_TOKEN
```

`-k` is acceptable only for this initial diagnostic when the FortiGate uses an
untrusted certificate. Configure TLS properly for production as described in
[Troubleshooting](TROUBLESHOOTING.md#tls-certificate-failure).

A successful response normally contains:

```json
{
  "status": "success",
  "results": {}
}
```

The real `results` object will contain licence data. Do not publish raw results
without removing serial numbers, internal addresses, and other deployment data.

## 5. Common API failures

| Result | Likely cause |
|---|---|
| HTTP 401 | Missing, incorrect, regenerated, or disabled token |
| HTTP 403 | Profile lacks permission, VDOM access is wrong, or Trusted Host does not match |
| HTTP 404 | FortiOS endpoint variant differs; the checker tries its fallback automatically |
| Timeout | Routing, firewall policy, HTTPS management access, or port mismatch |
| TLS error | Certificate is untrusted, expired, or does not match the configured hostname |

Official references:

- [Fortinet REST API administrator](https://docs.fortinet.com/document/fortigate/7.4.8/administration-guide/399023/rest-api-administrator)
- [Fortinet staff REST API Python example](https://community.fortinet.com/t5/FortiGate/Technical-Tip-Python-Script-Example-for-FortiGate-REST-API/ta-p/211989)
