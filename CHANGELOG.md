# Changelog — workspace-backup

## 1.0.0 (2026-06-17)
- Initial release. Derived from the `workspace-sync-backup` Tower book (+ Rin's live auto-commit / checkpoint scripts).
- `backup.sh` subcommands:
  - `snapshot` — git add+commit only on change; idle = clean no-op (no empty commits); secrets protected by `.gitignore`.
  - `checkpoint [create|list|restore|verify]` — save/restore critical workspace state with a sha256 manifest; `restore` backs up current state first.
  - `gc` — `git gc --prune=now` for loose-object bloat.
- Rin-specific paths generalized to env-overridable vars: `WORKSPACE_DIR`, `CHECKPOINT_DIR`, `CHECKPOINT_FILES`.
- PDA-structured: lean SKILL.md (body ≤100 lines) + `references/backup-guide.md` (one-way sync architecture, secret-staging gotcha, gc/prune, restore procedure, incident lessons).
