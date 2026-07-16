# workspace-backup

Keep an OpenClaw agent's workspace safe, recoverable, and synced — without losing or leaking anything. Derived from the `workspace-sync-backup` Tower book; packages the three jobs people conflate (backup vs sync vs visibility) into one tested helper.

## What you get
- **`scripts/backup.sh`** — one helper, three subcommands:
  - `snapshot` — `git add` + commit **only if the tree changed** (idle is a clean no-op, no empty commits). Relies on `.gitignore` to keep secrets out.
  - `checkpoint [create|list|restore|verify]` — save/restore a small set of critical files with a sha256 manifest; `restore` backs up the current state first.
  - `gc` — `git gc --prune=now` for loose-object bloat after a stray binary add.
- **`SKILL.md`** — quick-start + the backup-vs-sync-vs-visibility distinction + the `.gitignore` secret discipline.
- **`references/backup-guide.md`** — one-way sync diagram, secret-staging gotcha, gc/prune, restore procedure, incident lessons.

## Install
```bash
openclaw skills install git:rin-proxy/workspace-backup
```
Or copy the folder into `workspace/skills/`.

## Quick start
```bash
./scripts/backup.sh snapshot                       # commit ONLY if changed (run on a cron)
./scripts/backup.sh checkpoint create "pre-deploy" # save critical state before a risky change
./scripts/backup.sh checkpoint restore latest      # restore (current state backed up first)
./scripts/backup.sh checkpoint verify latest       # files + checksums vs manifest
./scripts/backup.sh gc                             # pack/prune loose objects
```

Paths are env-overridable: `WORKSPACE_DIR`, `CHECKPOINT_DIR`, `CHECKPOINT_FILES` (defaults suit a standard OpenClaw layout).

## Requires
`bash`, `git`. Runs fully local — no cloud calls. `snapshot` never force-commits and never runs destructive git ops; `checkpoint restore` is undoable (it snapshots current state first).
