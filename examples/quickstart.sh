#!/usr/bin/env bash
# Synthetic onboarding example; run from a reviewed checkout.
set -euo pipefail
umask 077
REPO="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
DEMO_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/rin-readme-workspace-backup.XXXXXX")"
WS="$DEMO_ROOT/workspace"
mkdir -p "$WS"
export OPENCLAW_WORKSPACE="$WS"
printf 'Example artifacts: %s\n' "$DEMO_ROOT"
bash "$REPO/scripts/install.sh" --workspace "$WS"
bash "$REPO/scripts/status.sh" --workspace "$WS"
printf '%s\n' 'ORCHID-731 original note' > "$WS/note.md"
bash "$REPO/scripts/backup.sh" checkpoint create readme-demo --workspace "$WS" --files note.md
bash "$REPO/scripts/backup.sh" checkpoint verify latest --workspace "$WS"
printf '%s\n' 'changed fixture' > "$WS/note.md"
bash "$REPO/scripts/backup.sh" checkpoint restore latest --workspace "$WS"
grep -q 'ORCHID-731 original note' "$WS/note.md"
printf 'Quickstart passed: %s (synthetic; see README for scope).\n' "workspace-backup"
