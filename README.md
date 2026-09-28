# workspace-backup

Create and verify local file checkpoints, take SQLite online backups, and restore selected workspace
files. Git snapshots and checkpoint archives are separate recovery mechanisms.

## Use and expected result

Before changing owned workspace files or practicing recovery. Select the full required file list
explicitly; default checkpoints are not a complete OpenClaw instance backup.

Example request: **“Create a checkpoint of the synthetic note, verify it, then demonstrate recovery
inside the test workspace.”**

Expected behavior: JSON reports status OK for creation and verification; restoring the fixture
recovers its original content.

The installer places this package in the explicit workspace. Current OpenClaw discovers its
`SKILL.md` directly and leaves `AGENTS.md` owner-controlled. The chat example is natural language, not a promise of a registered slash command.

## Quick start

From a reviewed checkout, run:

```bash
bash examples/quickstart.sh
```

The real local helper runs on synthetic data and checks the documented result. This is not an
assessment of production data or model answer quality. Success ends with `Quickstart passed:
workspace-backup`.

## Install and operate

This is a private repository. Authenticate with an account or GitHub App that has read access, and
never place a token in a clone URL, prompt or log. Check out the reviewed full commit before running
repository code:

```bash
git clone https://github.com/rin-proxy/workspace-backup.git
cd workspace-backup
REF=FULL_40_CHARACTER_COMMIT
git checkout --detach "$REF"
```

```bash
WS=/absolute/agent/workspace
bash scripts/install.sh --workspace "$WS"
bash scripts/status.sh --workspace "$WS"
OPENCLAW_WORKSPACE="$WS" bash scripts/backup.sh checkpoint create
OPENCLAW_WORKSPACE="$WS" bash scripts/backup.sh checkpoint verify
```

For a reviewed pinned update or recovery:

```bash
bash scripts/update.sh --workspace "$WS" --repo https://github.com/rin-proxy/workspace-backup.git --ref "$REF"
bash scripts/rollback.sh --workspace "$WS"
bash scripts/uninstall.sh --workspace "$WS"
```

## Operation and safety

Input: `--workspace` and required relative `--files`. Output: checkpoint directory, manifest hashes
and operation status. Missing required files or corrupt archives fail. Restore writes selected
workspace files and retains a pre-restore checkpoint where applicable.

`bash scripts/backup.sh checkpoint create LABEL --workspace DIR --files note.md`; `checkpoint verify
latest`; `checkpoint restore latest`. Repeat `--workspace DIR` for each command. `snapshot` uses
Git; `gc` performs Git maintenance.

Checkpoints and manifests are local. SQLite uses the online backup API; restore requires handling
active database writers. Snapshot creates a Git commit with a private index. No off-machine
replication or new schedule is enabled by installation. Keep credentials out of example commands and
reports. Use synthetic data for verification; preserve owner data during code maintenance.

Release evidence covers OpenClaw 2026.9.6. Bash, Python 3.11+, Git. Database fixtures use Python
sqlite3; no model provider. Revalidate changed SDK/native contracts before using another OpenClaw
version.

Recovery hint: Missing source → correct the required file list, then recreate and verify. Hash
mismatch → preserve the failed archive and use a verified checkpoint. Busy SQLite restore →
stop/checkpoint the intended test writer before retrying.

## Verification and evidence

```bash
bash test.sh
python3 scripts/check-docs.py
```

**Runtime evidence incomplete.** Strict success on the recorded synthetic battery was 9/12 before
and 10/12 after. Some attempted runs lack valid runtime evidence. They remain in the denominator;
the superiority claim is incomplete. Some strict differences involve rubric or representation
ambiguity; read the interpretation notes before drawing a substantive quality conclusion.

See [the full benchmark](BENCHMARK.md) for the exact comparison and limits. Installation alone does
not guarantee a better answer on every task.

Detailed documentation: [skill instructions](SKILL.md) · [acceptance and recovery](VERIFICATION.md)
· [tested compatibility](COMPATIBILITY.md) · [release notes](RELEASE-NOTES.md) ·
[changelog](CHANGELOG.md) · [commercial license](LICENSE-COMMERCIAL.md).
