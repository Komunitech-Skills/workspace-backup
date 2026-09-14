---
name: workspace-backup
description: Local workspace checkpoints with manifest verification, SQLite online backup and isolated restore.
version: 1.0.1
metadata:
  openclaw:
    emoji: "💾"
    requires:
      bins: ["bash", "python3", "git"]
triggers:
  - "back up my workspace"
  - "checkpoint state"
  - "snapshot"
  - "restore workspace"
  - "git gc"
author: Rin
license: UNLICENSED
lastUpdated: 2026-09-14
---

# Workspace backup

Keep recovery local unless the owner requests off-VPS replication. Preserve existing working backup schedules and distinguish backups from Git synchronization.

```bash
OPENCLAW_WORKSPACE=/absolute/workspace bash scripts/backup.sh checkpoint create pre-deploy
OPENCLAW_WORKSPACE=/absolute/workspace bash scripts/backup.sh checkpoint verify latest
OPENCLAW_WORKSPACE=/absolute/workspace bash scripts/backup.sh checkpoint restore latest
```

Set the required workspace-relative files with `CHECKPOINT_FILES` or `--files`; every required source must exist. The default list is not a full OpenClaw state backup. Full recovery also needs the selected state/config and agent databases, which the existing Rin backup system covers.

Checkpoint manifests are nonempty and schema-checked, with SHA-256 per file. SQLite sources use the online backup API. Verify before restore; active WAL/SHM writers must be stopped/checkpointed. Current files are backed up before restoration and failed copies roll back.

`snapshot` uses a private Git index, scans staged paths/content before commit, and preserves the owner's index on a rejected snapshot. Continue to ignore credentials, model binaries and generated state; heuristic scanning is not a guarantee that all secrets are detected. Sensitive filenames in historical Git do not alone establish exposure or require key rotation.

`gc` uses a two-week prune grace period under the helper lock. Keep logs outside the tracked workspace. Verify create → corrupt/reject → restore on synthetic files and a live SQLite fixture before relying on a new configuration.

For installation prerequisites and expected functional results, read [README.md](README.md) and [VERIFICATION.md](VERIFICATION.md). Installation alone does not establish runtime readiness.
