#!/bin/bash
# backup.sh — workspace-backup helper for an OpenClaw agent.
# Three jobs, one tool: snapshot (git commit-on-change), checkpoint (save/restore
# critical state), gc (pack loose objects). Derived from the workspace-sync-backup
# Tower book + Rin's live auto-commit / checkpoint scripts.
#
# Usage:
#   ./backup.sh snapshot                       # git add+commit ONLY if changed (idle = no-op)
#   ./backup.sh checkpoint create [reason]     # save critical files to a timestamped checkpoint
#   ./backup.sh checkpoint list                # list checkpoints, newest marked latest
#   ./backup.sh checkpoint restore <id|latest> # restore a checkpoint (backs up current first)
#   ./backup.sh checkpoint verify <id|latest>  # check files + sha256 vs manifest
#   ./backup.sh gc                             # git gc --prune=now (loose-object bloat)
#
# Env overrides (sane defaults shown):
#   WORKSPACE_DIR   workspace / git repo root        (default: /root/.openclaw/workspace)
#   CHECKPOINT_DIR  where checkpoints are stored      (default: $WORKSPACE_DIR/memory/checkpoints)
#   CHECKPOINT_FILES  space-separated relative paths to snapshot
#                     (default: the agent's core state — see below)
set -uo pipefail

WORKSPACE_DIR="${WORKSPACE_DIR:-/root/.openclaw/workspace}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-$WORKSPACE_DIR/memory/checkpoints}"
# Relative-to-WORKSPACE_DIR files captured by `checkpoint create`. Override for your layout.
CHECKPOINT_FILES="${CHECKPOINT_FILES:-memory/core-state.json memory/threads/main-thread.jsonl memory/active-tasks.md MEMORY.md}"
LATEST_LINK="$CHECKPOINT_DIR/latest"

die() { echo "❌ $*" >&2; exit 1; }

# --- snapshot: commit only on real change; idle = clean no-op (relies on .gitignore) ---
cmd_snapshot() {
  cd "$WORKSPACE_DIR" || die "workspace not found: $WORKSPACE_DIR"
  git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repo: $WORKSPACE_DIR (run 'git init' first)"
  if [ -z "$(git status --porcelain)" ]; then
    echo "✓ nothing changed — no commit (clean no-op)"
    return 0
  fi
  git add -A
  git commit -q -m "snapshot $(date -u +%Y-%m-%dT%H:%MZ)"
  echo "✅ snapshot committed: $(git log -1 --format='%h %s')"
}

# --- gc: pack/prune loose objects (e.g. after a stray binary add) ---
cmd_gc() {
  cd "$WORKSPACE_DIR" || die "workspace not found: $WORKSPACE_DIR"
  git rev-parse --git-dir >/dev/null 2>&1 || die "not a git repo: $WORKSPACE_DIR"
  echo "🧹 git gc --prune=now …"
  git gc --prune=now
  echo "✅ gc done"
}

# --- checkpoint: save/restore a small set of critical files (off the git path) ---
ckpt_create() {
  local reason="${1:-manual}" ts id dir hash count=0
  ts=$(date -u +%Y%m%d-%H%M%S); id="checkpoint-$ts"; dir="$CHECKPOINT_DIR/$id"
  mkdir -p "$dir"
  for rel in $CHECKPOINT_FILES; do
    if [ -f "$WORKSPACE_DIR/$rel" ]; then
      mkdir -p "$dir/$(dirname "$rel")"
      cp "$WORKSPACE_DIR/$rel" "$dir/$rel" && count=$((count+1))
    fi
  done
  {
    echo "{"
    echo "  \"checkpoint_id\": \"$id\","
    echo "  \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
    echo "  \"reason\": \"$reason\","
    echo "  \"files\": ["
    local first=1
    for rel in $CHECKPOINT_FILES; do
      [ -f "$dir/$rel" ] || continue
      hash=$(sha256sum "$dir/$rel" | cut -d' ' -f1)
      [ $first -eq 1 ] || echo ","
      first=0
      printf '    {"path": "%s", "sha256": "%s"}' "$rel" "$hash"
    done
    echo ""
    echo "  ]"
    echo "}"
  } > "$dir/manifest.json"
  rm -f "$LATEST_LINK"; ln -s "$dir" "$LATEST_LINK"
  echo "✅ checkpoint created: $id  ($count file(s), reason: $reason)"
  echo "   $dir/"
}

ckpt_list() {
  echo "=== Checkpoints ($CHECKPOINT_DIR) ==="
  local count=0 dir id ts
  for dir in "$CHECKPOINT_DIR"/checkpoint-*; do
    [ -d "$dir" ] || continue
    id=$(basename "$dir")
    ts=$(grep -m1 '"timestamp"' "$dir/manifest.json" 2>/dev/null | cut -d'"' -f4)
    echo "  $id   ${ts:-(no manifest)}"
    count=$((count+1))
  done
  [ "$count" -eq 0 ] && echo "  (none)"
  [ -L "$LATEST_LINK" ] && echo "  latest -> $(basename "$(readlink "$LATEST_LINK")")"
}

ckpt_resolve() {  # echo a real id, resolving 'latest'
  local id="$1"
  if [ "$id" = "latest" ]; then
    [ -L "$LATEST_LINK" ] || die "no latest checkpoint"
    basename "$(readlink "$LATEST_LINK")"
  else
    echo "$id"
  fi
}

ckpt_restore() {
  local id="$1"; [ -n "$id" ] || die "usage: checkpoint restore <id|latest>"
  id=$(ckpt_resolve "$id"); local dir="$CHECKPOINT_DIR/$id"
  [ -d "$dir" ] || die "checkpoint not found: $id"
  # Safety: snapshot current state before overwriting.
  local bdir="$CHECKPOINT_DIR/pre-restore-$(date -u +%Y%m%d-%H%M%S)"; mkdir -p "$bdir"
  for rel in $CHECKPOINT_FILES; do
    [ -f "$WORKSPACE_DIR/$rel" ] && { mkdir -p "$bdir/$(dirname "$rel")"; cp "$WORKSPACE_DIR/$rel" "$bdir/$rel"; }
  done
  echo "🔄 restoring $id (current state saved to $(basename "$bdir"))"
  while IFS= read -r rel; do
    [ -f "$dir/$rel" ] || continue
    mkdir -p "$WORKSPACE_DIR/$(dirname "$rel")"
    cp "$dir/$rel" "$WORKSPACE_DIR/$rel"
    echo "   restored $rel"
  done < <(grep -oE '"path": "[^"]+"' "$dir/manifest.json" 2>/dev/null | cut -d'"' -f4)
  echo "✅ restored from $id — ⚠️  verify files before continuing"
}

ckpt_verify() {
  local id="$1"; [ -n "$id" ] || die "usage: checkpoint verify <id|latest>"
  id=$(ckpt_resolve "$id"); local dir="$CHECKPOINT_DIR/$id"
  [ -d "$dir" ] || die "checkpoint not found: $id"
  local manifest="$dir/manifest.json"; [ -f "$manifest" ] || die "manifest missing for $id"
  echo "=== verify $id ==="
  local ok=1 rel want got
  while IFS= read -r line; do
    rel=$(echo "$line"  | sed -E 's/.*"path": "([^"]+)".*/\1/')
    want=$(echo "$line" | sed -E 's/.*"sha256": "([^"]+)".*/\1/')
    if [ ! -f "$dir/$rel" ]; then echo "  ⚠️  $rel (missing)"; ok=0; continue; fi
    got=$(sha256sum "$dir/$rel" | cut -d' ' -f1)
    if [ "$got" = "$want" ]; then echo "  ✅ $rel"; else echo "  ❌ $rel CHECKSUM MISMATCH"; ok=0; fi
  done < <(grep -oE '"path": "[^"]+", "sha256": "[^"]+"' "$manifest")
  [ "$ok" -eq 1 ] && echo "✅ checkpoint $id is valid" || die "checkpoint $id FAILED verification"
}

cmd_checkpoint() {
  case "${1:-}" in
    create)  shift; ckpt_create "${1:-manual}" ;;
    list)    ckpt_list ;;
    restore) shift; ckpt_restore "${1:-}" ;;
    verify)  shift; ckpt_verify "${1:-}" ;;
    *) die "usage: checkpoint [create|list|restore|verify]" ;;
  esac
}

case "${1:-}" in
  snapshot)   cmd_snapshot ;;
  checkpoint) shift; cmd_checkpoint "$@" ;;
  gc)         cmd_gc ;;
  *)
    cat >&2 <<EOF
workspace-backup — snapshot · checkpoint · gc
  ./backup.sh snapshot                       commit ONLY if changed (idle = no-op)
  ./backup.sh checkpoint create [reason]     save critical state
  ./backup.sh checkpoint list                list checkpoints
  ./backup.sh checkpoint restore <id|latest> restore (backs up current first)
  ./backup.sh checkpoint verify  <id|latest> verify files + checksums
  ./backup.sh gc                             git gc --prune=now
EOF
    exit 1 ;;
esac
