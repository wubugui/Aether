#!/usr/bin/env bash
set -euo pipefail
ROOT=/workspace/scratch/a29d03198654
REPO="$ROOT/Aether"
PROJECT="$REPO/candidates/round40-exclusive-20260930/project"
SELF=$(readlink -f "${BASH_SOURCE[0]}")
exec 9>"$ROOT/tools-feiting/cloudsea52e-build.lock"
flock -n 9 || { echo '52e build already running; refusing duplicate'; exit 3; }
test -n "${DISPLAY:-}" || { echo 'Launch from existing cloud desktop terminal; actual renderer required'; exit 2; }
test ! -e "$PROJECT/scenes/candidate52e/Game52e.tscn" || { echo '52e candidate exists; refuse overwrite or rebuild'; exit 2; }
cd "$REPO"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$REPO/cloud-evidence/cloudsea52e-build-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" > "$ROOT/tools-feiting/feiting52e-build-last.txt"
printf '%s\n' "$$" > "$OUT/wrapper.pid"
cp "$SELF" "$OUT/run.sh"
cp "$PROJECT/tools/build_cloudsea52e.gd" "$PROJECT/tools/cloudsea52e_audit.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$OUT/"
cp "$REPO/cloud-evidence/cloudsea52e-integration-preparation/integration-manifest.json" "$OUT/"
sha256sum "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/project.godot" "$PROJECT/tools/build_cloudsea52e.gd" "$PROJECT/tools/cloudsea52e_audit.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$REPO/source-assets/cloud-sea52e/cloud_sea_52e_0.glb" "$REPO/source-assets/cloud-sea52e/cloud_sea_52e_1.glb" "$REPO/source-assets/cloud-sea52e/cloud_sea_52e_2.glb" > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/build_cloudsea52e.gd -- --report-dir="$OUT" > "$OUT/build.stdout.log" 2> "$OUT/build.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/build.exit-code.txt"
cat "$OUT/build.stdout.log"
cat "$OUT/build.stderr.log" >&2
if rg -n 'SCRIPT ERROR:|^ERROR:|Leak|leak' "$OUT/build.stdout.log" "$OUT/build.stderr.log" > "$OUT/log-gate.txt"; then CODE=1; fi
printf '%s\n' "$CODE" > "$OUT/wrapper.exit-code.txt"
printf '52e build exit %s; %s\n' "$CODE" "$OUT"
exit "$CODE"
