# Publishing to GitHub

Recommended repository name:

```text
librenms-fortigate-license-checker
```

Suggested description:

```text
FortiGate REST API licence and support-contract checker for LibreNMS Services.
```

## 1. Create an empty GitHub repository

Do not initialize it with a README, `.gitignore`, or licence. Those choices are
already handled locally, and this project intentionally has no licence file.

## 2. Initialize the local repository

Open Git Bash or PowerShell inside the extracted project folder:

```bash
git init
git branch -M main
git add .
```

## 3. Preserve Linux executable permissions from Windows

Windows extraction can remove Linux executable permissions. Record them in the
Git index after `git add .` and before the first commit:

```bash
git update-index --chmod=+x plugins/check_fortigate_license
git update-index --chmod=+x scripts/install.sh
git update-index --chmod=+x scripts/preflight.sh
git update-index --chmod=+x scripts/check_repository.sh
```

Verify that each mode is `100755`:

```bash
git ls-files --stage | grep -E 'check_fortigate_license|scripts/.*\.sh'
```

## 4. Validate before committing

```bash
./scripts/check_repository.sh
```

If Git Bash cannot execute it yet:

```bash
bash scripts/check_repository.sh
```

## 5. Commit and publish

```bash
git commit -m "Initial release: LibreNMS FortiGate licence checker"
git remote add origin \
  https://github.com/YOUR-USERNAME/librenms-fortigate-license-checker.git
git push -u origin main
```

Configure identity first if Git asks:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Non-fast-forward push rejection

This normally means the GitHub repository was initialized or changed remotely.
If the remote contains work you want to keep:

```bash
git pull --rebase origin main
git push -u origin main
```

If the remote contains an accidental auto-generated initial commit, inspect it
before deciding whether to recreate the empty GitHub repository. Do not force
push unless you deliberately intend to replace remote history.

## Public-release safety checklist

- No real API token or per-device JSON configuration.
- No internal IP address, hostname, email address, organization name, or serial.
- No raw FortiGate response containing deployment identifiers.
- All shell scripts and the plugin are mode `100755`.
- Repository validation and GitHub Actions pass.
- The absence of an open-source licence is intentional and understood.
