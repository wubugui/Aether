#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspace/scratch/a29d03198654
REPO="$ROOT/Aether"
PROJECT="$REPO/candidates/round40-exclusive-20260930/project"
PREP="$REPO/cloud-evidence/cloudsea52e-integration-preparation"
SELF=$(readlink -f "${BASH_SOURCE[0]}")
exec 9>"$ROOT/tools-feiting/cloudsea52e-verify.lock"
flock -n 9 || { echo '52e paired verification already running; refusing duplicate'; exit 3; }
test -n "${DISPLAY:-}" || { echo 'Use existing cloud desktop terminal; actual renderer required'; exit 2; }
test -e "$PROJECT/scenes/candidate52e/build-report-52e.json" || { echo 'Verified native52e build required'; exit 2; }
cd "$REPO"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$REPO/cloud-evidence/cloudsea52e-paired-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" > "$ROOT/tools-feiting/feiting52e-verify-last.txt"
printf '%s\n' "$$" > "$OUT/wrapper.pid"
cp "$SELF" "$OUT/run.sh"
cp "$PREP/compare_pair52e.py" "$OUT/"
cp "$PROJECT/tools/verify_cloudsea52e.gd" "$PROJECT/tools/cloudsea52e_audit.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/scenes/candidate52e/build-report-52e.json" "$OUT/"
sha256sum "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/scenes/candidate52e/Game52e.tscn" "$PROJECT/project.godot" "$PROJECT/tools/verify_cloudsea52e.gd" "$PROJECT/tools/cloudsea52e_audit.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" > "$OUT/input-sha256.txt"
FINAL=0
for VERSION in 51b 52e; do
  set +e
  "$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_cloudsea52e.gd -- --version="$VERSION" --output-dir="$OUT/$VERSION" > "$OUT/$VERSION.stdout.log" 2> "$OUT/$VERSION.stderr.log"
  CODE=$?
  printf '%s\n' "$CODE" > "$OUT/$VERSION.exit-code.txt"
  cat "$OUT/$VERSION.stdout.log"
  cat "$OUT/$VERSION.stderr.log" >&2
  if [[ "$CODE" != 0 ]]; then FINAL=1; fi
  if rg -n 'SCRIPT ERROR:|^ERROR:|Leak|leak' "$OUT/$VERSION.stdout.log" "$OUT/$VERSION.stderr.log" > "$OUT/$VERSION.log-gate.txt"; then FINAL=1; fi
  set -e
done
set +e
python "$OUT/compare_pair52e.py" "$OUT" > "$OUT/compare.log" 2>&1
CODE=$?
printf '%s\n' "$CODE" > "$OUT/compare.exit-code.txt"
cat "$OUT/compare.log"
if [[ "$CODE" != 0 ]]; then FINAL=1; fi
printf '%s\n' "$FINAL" > "$OUT/wrapper.exit-code.txt"
printf '52e paired verification exit %s; %s\n' "$FINAL" "$OUT"
exit "$FINAL"
