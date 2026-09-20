# Contributing

## Development checks

```bash
./scripts/check_repository.sh
```

The project supports Python 3.10, 3.11, and 3.12 and uses only the standard
library.

## Pull requests

- Keep API parsing compatible with existing flat and nested support results.
- Add tests for new response shapes or status logic.
- Preserve Nagios exit codes: 0 OK, 1 Warning, 2 Critical, 3 Unknown.
- Do not add third-party runtime dependencies without a strong reason.
- Use British spelling `licence` in user-facing checker messages for consistency.
- Sanitize all samples and logs.

Never include a live token, internal address, hostname, organization name,
serial number, or protected configuration file.
