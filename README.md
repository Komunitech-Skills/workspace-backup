# workspace-backup

Create and verify local file checkpoints, take SQLite online backups, and restore selected workspace files. Git snapshots and checkpoint archives are separate recovery mechanisms.

Navigation: [When to use it](#when-to-use-it) · [See the expected result](#see-the-expected-result) · [Quick start on synthetic data](#quick-start-on-synthetic-data) · [Using it from OpenClaw](#using-it-from-openclaw) · [Input, output and completion](#input-output-and-completion) · [Commands and configuration](#commands-and-configuration) · [Data and effects](#data-and-effects) · [Get the private repository](#get-the-private-repository) · [Compatibility](#compatibility) · [Install and verify](#install-and-verify) · [Update, rollback and remove](#update-rollback-and-remove) · [Validation](#validation) · [Shared installer source](#shared-installer-source) · [Troubleshooting](#troubleshooting) · [Related products and further reading](#related-products-and-further-reading)

## When to use it

Before changing owned workspace files or practicing recovery. Select the full required file list explicitly; default checkpoints are not a complete OpenClaw instance backup.

## See the expected result

Example request: **“Create a checkpoint of the synthetic note, verify it, then demonstrate recovery inside the test workspace.”**

Expected behavior: JSON reports status OK for creation and verification; restoring the fixture recovers its original content. This is an illustrative acceptance scenario, not a captured production conversation.

## Quick start on synthetic data

After obtaining a reviewed checkout using [private access](#get-the-private-repository), run:

```bash
bash examples/quickstart.sh
```

The script creates a private temporary workspace, prints its artifact directory and checks the result. Read [the example](examples/quickstart.sh) before running it. It keeps the synthetic artifacts for inspection; remove only the printed example directory when finished. It does not target your existing workspace or enable production services.

**What this example proves:** The real local helper runs on synthetic data and checks the documented result. This is not an assessment of production data or model answer quality.

Success ends with `Quickstart passed: workspace-backup`; an unexpected result exits nonzero. Some examples deliberately provoke a failure and verify it is rejected. Run installation and the relevant functional probe below for your own selected instance.

## Using it from OpenClaw

The installer places this package under `skills/workspace-backup` in the explicit workspace and adds its managed instruction pointer. Ask the agent in that workspace to read the matching SKILL.md and follow it. The chat example is natural language, not a promise of a registered slash command.

## Input, output and completion

Input: `--workspace` and required relative `--files`. Output: checkpoint directory, manifest hashes and operation status. Missing required files or corrupt archives fail. Restore writes selected workspace files and retains a pre-restore checkpoint where applicable.

Typical workflow: select the intended input/workspace → inspect prerequisites → run the matching operation → inspect its real result and artifact → report success, missing evidence or failure. JSON reports status OK for creation and verification; restoring the fixture recovers its original content.

## Commands and configuration

`bash scripts/backup.sh checkpoint create LABEL --workspace DIR --files note.md`; `checkpoint verify latest`; `checkpoint restore latest`. Repeat `--workspace DIR` for each command. `snapshot` uses Git; `gc` performs Git maintenance.

## Data and effects

Checkpoints and manifests are local. SQLite uses the online backup API; restore requires handling active database writers. Snapshot creates a Git commit with a private index. No off-machine replication or new schedule is enabled by installation. Keep credentials out of example commands and reports. Use synthetic data for verification; preserve owner data during code maintenance.

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

Release evidence covers OpenClaw 2026.9.3. Bash, Python 3.11+, Git. Database fixtures use Python sqlite3; no model provider. Revalidate changed SDK/native contracts before using another OpenClaw version.

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

## Troubleshooting

Missing source → correct the required file list, then recreate and verify. Hash mismatch → preserve the failed archive and use a verified checkpoint. Busy SQLite restore → stop/checkpoint the intended test writer before retrying.

Private clone returns 404 → check the authenticated account and repository read permission on this machine → repeat checkout. Installation rejected → inspect the reported workspace/ownership/drift conflict → resolve that exact cause and rerun status. A successful install receipt alone is not functional evidence; repeat the acceptance probe after recovery.

## Related products and further reading

[safe-update](https://github.com/rin-proxy/safe-update) · [workspace-maintenance](https://github.com/rin-proxy/workspace-maintenance). The [runbook catalog](https://github.com/rin-proxy/rin-runbook/blob/main/CATALOG.md) identifies active sources and presets. skill-curator is archived; new skill-management installs use skill-forge.

[Skill instructions](SKILL.md) · [Acceptance and recovery](VERIFICATION.md) · [Changelog](CHANGELOG.md) · [Commercial license](LICENSE-COMMERCIAL.md). Follow the repository's actual license/metadata and owner-granted access; this guide introduces no new license or redistribution grant. Detailed agent procedures stay in their existing reference files so discovery instructions remain concise.

## Release and maintenance checks

See [release notes](RELEASE-NOTES.md) and [tested compatibility](COMPATIBILITY.md).
Run `python3 scripts/check-docs.py` to validate local documentation links and declared interfaces;
CI also runs the synthetic quickstart. Private GitHub access is required to download releases.
