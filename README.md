# workspace-backup

Local checkpoints with strict required-file manifests, hashes, verified restore and SQLite online backups. Git snapshots use a private index and a pre-commit secret gate. Retain the existing Rin backup schedule; off-VPS copies are not required.

## Get the private repository

Use an account or GitHub App with **read access** to this repository. Configure authentication on the machine running OpenClaw; a successful login on another machine does not transfer access. For an existing GitHub CLI login:

```bash
gh auth status
gh auth setup-git
gh repo clone rin-proxy/workspace-backup
cd workspace-backup
git fetch origin main
# Set REF to the reviewed full commit from the release manifest or PR.
REF=FULL_40_CHARACTER_COMMIT
git checkout --detach "$REF"
```

The placeholder must be replaced before execution. Do not paste tokens into clone URLs, agent prompts, config examples or logs. HTTPS updates below use the configured Git credential helper. A 404 on a private repo can mean missing access: check the account and repository permission first. Run installer commands from this checkout; `WS` always selects the target agent workspace explicitly.

## Compatibility

Validated against OpenClaw 2026.9.3. Linux, Bash, Git and Python 3.11+ are required for the operational lifecycle. JavaScript components require Node 22.13+; the runtime SDK tests use Node 24. Revalidate SDK contracts before upgrading OpenClaw.

## Install and verify

Select an existing workspace explicitly; do not point a test at production. Review and check out the intended full commit before running its installer.

```bash
WS=/absolute/agent/workspace
bash scripts/install.sh --workspace "$WS"
bash scripts/status.sh --workspace "$WS"
OPENCLAW_WORKSPACE="$WS" bash scripts/backup.sh checkpoint create
OPENCLAW_WORKSPACE="$WS" bash scripts/backup.sh checkpoint verify
```

## Update, rollback and remove

```bash
bash scripts/update.sh --workspace "$WS" --repo https://github.com/rin-proxy/workspace-backup.git --ref "$REF"
bash scripts/rollback.sh --workspace "$WS"
bash scripts/uninstall.sh --workspace "$WS"
```

Install/reinstall is idempotent. Updates refuse unreviewed code drift; `--force` is an explicit override after review. Rollback refuses conflicting owner edits to `AGENTS.md`. Uninstall archives owned code outside discovery and preserves owner memory/configuration. `--keep-code` only removes the instruction pointer, so the skill remains discoverable. Installation status always separates code presence from runtime verification.

## Validation

```bash
bash test.sh
```

This entrypoint runs provider-free tests in temporary workspaces with a clean HOME and no inherited service credentials. Exit 0 means the listed tests passed; optional native tests print SKIPPED when dependencies are absent. It does not prove live model quality, delivery, or production readiness. See [VERIFICATION.md](VERIFICATION.md) for functional acceptance criteria, expected results and failure handling. CI runs this same entrypoint on Python 3.11 and Node 24. Recheck real SDK/native/model integration separately when changing those components.

## Shared installer source

Lifecycle code is generated from the reviewed skill-forge core; `vendor.json` records
source commits and file hashes. Run `python3 scripts/vendor.py check` to detect drift.
Keep this manifest with the package. Installation and pinned updates remain standalone;
no mutable upstream branch is fetched at runtime.

A suite-owned component can move to standalone ownership using
`bash scripts/install.sh --workspace /absolute/workspace --adopt-suite` after reviewing
the change. The transfer requires the suite's recorded code to be unchanged. Suite
rollback/uninstall will then preserve that standalone component. To return to suite
ownership, uninstall the standalone package (data remains preserved), then explicitly
install the selected suite component. Ordinary update/rollback commands remain available.
