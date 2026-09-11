# workspace-backup

Local checkpoints with strict required-file manifests, hashes, verified restore and SQLite online backups. Git snapshots use a private index and a pre-commit secret gate. Retain the existing Rin backup schedule; off-VPS copies are not required.

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
bash scripts/update.sh --workspace "$WS" --repo https://github.com/rin-proxy/workspace-backup.git --ref FULL_40_CHARACTER_COMMIT
bash scripts/rollback.sh --workspace "$WS"
bash scripts/uninstall.sh --workspace "$WS"
```

Install/reinstall is idempotent. Updates refuse unreviewed code drift; `--force` is an explicit override after review. Rollback refuses conflicting owner edits to `AGENTS.md`. Uninstall archives owned code outside discovery and preserves owner memory/configuration. `--keep-code` only removes the instruction pointer, so the skill remains discoverable. Installation status always separates code presence from runtime verification.

## Validation

Run the repository tests against synthetic fixtures; inspect commands before using live credentials. Python tests: `python3 -m unittest discover -s tests -p "test_*.py"` where present. JavaScript tests are in `test/`, `tests/`, or `_semantic-stack/test-*.mjs`. Include install → reinstall → pinned update → rollback → uninstall, owner-data preservation, failure paths and a real OpenClaw integration test. No service or scheduler is enabled by the common skill installer.

The detailed agent procedure remains in `SKILL.md` where present. The compatibility and lifecycle instructions in this README describe the current implementation.
