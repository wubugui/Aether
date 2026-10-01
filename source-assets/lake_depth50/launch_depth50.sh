#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$PWD/cloud-evidence/depth50-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting50-last.txt"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
GODOT="$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/build_lake_depth50.gd" "$PROJECT/tools/verify_lake_depth50.gd" "$PROJECT/scripts/lake_depth50.gd" "$PROJECT/assets/lake_depth50/lake_water_depth50.gdshader" "$PWD/source-assets/lake_depth50/shader-change-ledger.json" "$OUT/"
sha256sum "$PROJECT/scenes/candidate49/Game49.tscn" "$PROJECT/tools/build_lake_depth50.gd" "$PROJECT/tools/verify_lake_depth50.gd" "$PROJECT/scripts/lake_depth50.gd" "$PROJECT/assets/lake_depth50/lake_water_depth50.gdshader" "$PWD/source-assets/lake50-intake/height49-1m-rf.res" "$PWD/source-assets/lake50-intake/patch025/"*-height025-rf.res > "$OUT/input-sha256.txt"
set +e
"$GODOT" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/build_lake_depth50.gd -- --diagnostic-dir="$OUT" > "$OUT/build.stdout.log" 2> "$OUT/build.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/build.exit-code.txt"
cat "$OUT/build.stdout.log";cat "$OUT/build.stderr.log" >&2
if [ "$CODE" != 0 ]; then exit "$CODE"; fi
"$GODOT" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_lake_depth50.gd -- --output-dir="$OUT/images" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log";cat "$OUT/verify.stderr.log" >&2
printf 'Game50 depth-only limited validation exit %s; evidence %s; not total visual or motion acceptance\n' "$CODE" "$OUT"
exit "$CODE"
