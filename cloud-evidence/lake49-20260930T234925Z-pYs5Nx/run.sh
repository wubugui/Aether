#!/usr/bin/env bash
set -euo pipefail
cd /workspace/scratch/a29d03198654/Aether
export XDG_CACHE_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/cache
export XDG_DATA_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/data
export XDG_CONFIG_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/config
OUT=$(mktemp -d "$PWD/cloud-evidence/lake49-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee /workspace/scratch/a29d03198654/tools-feiting/feiting49-last.txt
GODOT=/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
PAYLOAD="$PWD/source-assets/lake49/lake49-payload.json"
cp "$PROJECT/tools/build_cloud_lake49.gd" "$OUT/"
cp "$PROJECT/tools/verify_cloud_lake49.gd" "$OUT/"
cp "$0" "$OUT/run.sh"
sha256sum "$PAYLOAD" "$PROJECT/scenes/candidate48/Game48.tscn" > "$OUT/input-sha256.txt"
set +e
"$GODOT" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/build_cloud_lake49.gd -- --payload="$PAYLOAD" --diagnostic-dir="$OUT" > "$OUT/build.stdout.log" 2> "$OUT/build.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/build.exit-code.txt"
cat "$OUT/build.stdout.log"; cat "$OUT/build.stderr.log" >&2
if [ "$CODE" != 0 ]; then exit "$CODE"; fi
"$GODOT" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_cloud_lake49.gd -- --payload="$PAYLOAD" --output-dir="$OUT/images" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log"; cat "$OUT/verify.stderr.log" >&2
printf 'Lake49 limited geometry/runtime execution outcome %s; raw evidence: %s (not reference or required-motion acceptance)\n' "$CODE" "$OUT"
exit "$CODE"
