# Backup Guide

Full reference for the `workspace-backup` skill — loaded on demand to keep the SKILL.md body lean. Deep theory: `tower/workspace-sync-backup.md`.

## The git one-way sync architecture

```
┌────────────────────────────┐        git pull         ┌─────────────────────────┐
│  VPS  (LIVE — source)      │  ───────────────────►   │  Clone (backup copy)    │
│  the agent runs here 24/7  │                          │  you read it in a UI    │
└────────────────────────────┘   ◄── push? (DON'T) ──   └─────────────────────────┘
```

- **The source of truth is the box the agent runs on** — it writes there.
- **The clone pulls** (an editor's git plugin, or a cron `git pull`) on an interval. It is where a human reads/curates.
- **Flow is ONE-WAY: source → clone.** The clone should not push back. A non-bare server with `receive.denyCurrentBranch=refuse` rejects a push anyway — that is correct, not a bug. One-way avoids merge chaos and keeps a single authority.

### The 2-step truth (the gotcha that eats agents alive)

A change on the source reaches the clone only if **both** happen: (1) it is **committed** on the source, and (2) the clone **pulls**. `git pull` only moves commits — never the uncommitted working tree. If the agent writes files but nothing commits them, they never sync, no matter how long you wait. (A real incident: 15 of an agent's changes sat uncommitted, invisible to the backup, because the box had no auto-commit.)

`backup.sh snapshot` is fix step 1 — the commit half. Put it on a cron (`*/30 * * * *`) so writes actually flow. With snapshot every 30 min + a pull every 60 min, writes reach the clone in **< 1.5 h** automatically.

## The .gitignore secret-staging gotcha

`git add -A` (inside `snapshot`) stages **everything not ignored**. On an agent box that is a live grenade: a real `.env` with exchange API keys was once caught staged for commit because `.gitignore` had a single line. Before `snapshot` is ever scheduled, ignore at minimum:

- **secrets** — `.env`, `*.key`, credential files, token files
- **dependencies** — `node_modules/`, venvs, model runtimes, browser binaries
- **generated** — search/embedding indexes, caches, logs

Then **verify**: `git log --all -- .env` must be empty (the secret was never committed). The skill relies entirely on `.gitignore` for secret protection — `snapshot` does not inspect file contents.

### Don't loop your own log

If you redirect `snapshot`'s cron output to a log, write it **outside** the workspace (e.g. `/var/log/agent-snapshot.log`). A log written *inside* the workspace is itself a change → the next `snapshot` commits the log → which grows it → which commits again → an infinite churn of commits.

## Repo hygiene — git gc / prune

A runaway `git add` of binaries once left **756 MB of loose objects** in `.git`. Pack and prune them:

```bash
./scripts/backup.sh gc        # wraps: git gc --prune=now
```

The durable fix is to keep big regenerable artifacts (dependencies, indexes, model files) out of git entirely via `.gitignore`, so the repo stays a **text history**, not a binary dump.

## Checkpoints — save / restore procedure

Checkpoints are a fast, off-git safety net for a small set of **critical** files (agent core state, the main thread, active tasks, top-level memory). They complement git history; they do not replace it.

```bash
./scripts/backup.sh checkpoint create "pre-migration"   # snapshot critical files + sha256 manifest
./scripts/backup.sh checkpoint list                     # newest is symlinked as 'latest'
./scripts/backup.sh checkpoint verify latest            # files present + checksums match manifest
./scripts/backup.sh checkpoint restore latest           # copy files back into the workspace
```

**Restore is safe by construction:** before overwriting anything, `restore` copies the *current* live files into a `pre-restore-<timestamp>/` checkpoint. So a restore is itself undoable. After restoring, **verify the files are correct before continuing** — a restore reverts state, which can surprise a running agent.

Which files are captured is controlled by `CHECKPOINT_FILES` (space-separated, relative to `WORKSPACE_DIR`). Override it for a non-standard layout; the default targets a standard OpenClaw memory layout.

## Layer your safety net

Three independent copies cover three failure modes:

1. **Git history** (commits via `snapshot`) — fine-grained "what changed when," recoverable per file.
2. **Checkpoints / off-box archive** — a periodic `tar` of the workspace to separate storage survives the box itself dying. Backup ≠ sync — keep both.
3. **The clone** — a second physical copy on another machine.

## Verify the loop actually works

Don't trust it — test it end to end:

```bash
# on the source:
git log -1 --format='%h %s'          # did snapshot fire? look for the snapshot commit
# on the clone (after a pull):
git cat-file -e <that-hash> && echo "synced ✓"
```

If the snapshot commit exists on the clone, the full loop (write → commit → pull) is live.

## Incident lessons (condensed)

- **Uncommitted ≠ synced.** 15 changes sat invisible because nothing committed them. → schedule `snapshot`.
- **Tarball ≠ commit.** Daily archives existed while sync never moved. → keep both, and verify the commit.
- **One `.gitignore` line ≠ safe.** A real `.env` was caught staged. → ignore broadly, then `git log --all -- .env`.
- **Binaries bloat `.git`.** 756 MB of loose objects from a stray add. → ignore big regenerables + `gc`.
- **A log inside the repo loops.** → log outside the workspace.

---
*Derived from the `workspace-sync-backup` Tower book. By Rin 💾*
