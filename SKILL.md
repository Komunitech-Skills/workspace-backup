---
name: workspace-backup
description: Keep an OpenClaw agent's workspace safe, recoverable, and synced — one helper for git snapshot (commit-on-change, idle no-op), state checkpoints (save/restore/verify), and repo gc. Encodes the backup-vs-sync-vs-visibility distinction and the .gitignore secret trap. Use when you back up a workspace, checkpoint state before a risky change, or a runaway add bloats the repo.
version: 1.0.0
metadata:
  openclaw:
    emoji: "💾"
    requires:
      bins: ["bash", "git"]
triggers:
  - "back up my workspace"
  - "checkpoint state"
  - "snapshot"
  - "restore workspace"
  - "git gc"
author: Rin
license: UNLICENSED
lastUpdated: 2026-06-17
---

# Workspace Backup

Keep an agent's workspace safe, recoverable, and synced — without losing or leaking anything. One helper covers the three jobs people conflate.

## 🚀 Quick Start

```bash
./scripts/backup.sh snapshot                       # git add+commit ONLY if changed (idle = no-op)
./scripts/backup.sh checkpoint create "pre-deploy" # save critical state to a timestamped checkpoint
./scripts/backup.sh checkpoint list                # list checkpoints (newest marked latest)
./scripts/backup.sh checkpoint restore latest      # restore (current state is backed up first)
./scripts/backup.sh checkpoint verify latest       # check files + sha256 vs manifest
./scripts/backup.sh gc                             # git gc --prune=now (loose-object bloat)
```

Paths are env-overridable — `WORKSPACE_DIR`, `CHECKPOINT_DIR`, `CHECKPOINT_FILES` (defaults suit a standard OpenClaw layout).

## 🧭 Backup vs sync vs visibility (don't conflate)

Three different problems, three different mechanisms:

- **Backup** = a recoverable copy if disaster strikes (a checkpoint, or a tarball off-box).
- **Sync** = commits flowing between two live copies (git pull/push).
- **Visibility** = a human reading the agent's state in a nice UI.

Confusing them is why people *think* they have a backup when they have none. A nightly tarball is **not** a git commit, and `git pull` only moves **commits** — never an uncommitted working tree. So a change syncs only if it is **committed** on the source **and** the clone **pulls**. `snapshot` is the commit half: run it on a cron so writes actually flow.

Architecture is **one-way: source → clone** (the VPS runs the agent; the clone pulls and never pushes back). See references for the full diagram.

## 🔒 The .gitignore secret discipline

`snapshot` runs `git add -A`, which commits **everything not ignored** — a live grenade on an agent box. Before you ever enable it, `.gitignore` must cover:

- **secrets** — `.env`, `*.key`, credential files
- **dependencies** — `node_modules/`, venvs, model/browser binaries
- **generated** — search indexes, caches, logs

Then verify a secret was never committed: `git log --all -- .env` should be **empty**. `snapshot` relies entirely on `.gitignore` for this — it does not scan content.

## ✅ When to use

- **Before any risky change** (big edit, migration, runaway-script risk) → `checkpoint create`.
- **On a schedule** → `snapshot` every ~30 min via cron so writes reach your backup clone.
- **After a stray binary `add`** bloated `.git` → `gc`.
- **Recovering** a clobbered state → `checkpoint restore` (then verify).

Two non-obvious rules baked in: `snapshot` is a **clean no-op when idle** (no empty commits), and if you log its cron output, write the log **outside** the workspace (a log inside it is a change → next snapshot commits it → loop).

→ Full reference (one-way sync diagram · secret-staging gotcha · gc/prune · restore procedure · incident lessons): [`references/backup-guide.md`](references/backup-guide.md) · deep theory: `tower/workspace-sync-backup.md`.

---
*Derived from the `workspace-sync-backup` Tower book. By Rin 💾*
