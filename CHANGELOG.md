# Changelog

## 2026-09-14 — Audit acceptance

- Document private-repository access, explicit prerequisites, functional expectations and recovery limits.
- Add one offline test entrypoint and CI; distinguish runtime/behavior evidence from installation status.


## 2026-09-11 integration remediation

Local checkpoints with strict required-file manifests, hashes, verified restore and SQLite online backups. Git snapshots use a private index and a pre-commit secret gate. Retain the existing Rin backup schedule; off-VPS copies are not required.

Explicit workspace selection, reversible lifecycle and regression coverage; install status does not imply runtime readiness.

— workspace-backup

## 1.0.0 (2026-06-17)
- Initial release. Derived from the `workspace-sync-backup` Tower book (+ Rin's live auto-commit / checkpoint scripts).
- `backup.sh` subcommands:
  - `snapshot` — git add+commit only on change; idle = clean no-op (no empty commits); secrets protected by `.gitignore`.
  - `checkpoint [create|list|restore|verify]` — save/restore critical workspace state with a sha256 manifest; `restore` backs up current state first.
  - `gc` — `git gc --prune=now` for loose-object bloat.
- Rin-specific paths generalized to env-overridable vars: `WORKSPACE_DIR`, `CHECKPOINT_DIR`, `CHECKPOINT_FILES`.
- PDA-structured: lean SKILL.md (body ≤100 lines) + `references/backup-guide.md` (one-way sync architecture, secret-staging gotcha, gc/prune, restore procedure, incident lessons).
