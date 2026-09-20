# Operations

## Thresholds

The service parameters control days remaining:

```text
-w 60 -c 30
```

The constraints are:

```text
0 <= critical <= warning
```

## Status-pattern policy

Each JSON file can classify FortiOS status text with shell-style wildcards:

```json
"critical_status_patterns": [
  "*expired*",
  "*invalid*",
  "*revoked*"
],
"warning_status_patterns": [
  "*warning*",
  "*expiring*"
]
```

Pattern matching is case-insensitive. Do not add `*no_license*` unless every
unlicensed optional feature should make the whole service Critical.

## Ignoring intentionally irrelevant items

First review the exact API names shown in the Services message, then add only
approved exclusions:

```json
"ignore_features": [
  "fortianalyzer_cloud*",
  "* / unused_support_contract"
]
```

Wildcards are case-insensitive. Keep the list empty unless an item is genuinely
out of scope; an exclusion hides it from both output and severity evaluation.

## Rotate an API token

1. Generate a replacement token on that FortiGate.
2. Edit only the corresponding protected JSON file.
3. Validate JSON and permissions.
4. Test as the `librenms` user.
5. Poll services in debug mode.
6. Revoke the old token after successful verification.

Never paste a token into a service parameter or shell command.

## Update the checker

From a reviewed repository checkout:

```bash
git pull --ff-only
./scripts/check_repository.sh
sudo ./scripts/install.sh
```

Then test one device and run:

```bash
cd /opt/librenms
sudo -u librenms ./check-services.php -d
```

Updating the plugin does not overwrite per-device JSON files.

## Routine checks

- Review Unknown services promptly; they indicate monitoring failure.
- Review Warning and Critical output against procurement/renewal records.
- Periodically verify Trusted Hosts and remove obsolete API administrators.
- Rotate API tokens according to organizational policy.
- Move from `verify_tls: false` to verified TLS when certificate management is ready.
- Back up configuration securely, never in a public repository.
