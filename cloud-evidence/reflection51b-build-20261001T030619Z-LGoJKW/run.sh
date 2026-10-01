#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51b-build-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51b-build-last.txt"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/build_lake_reflection51b.gd" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/assets/reflection51b/lake_water_reflection51b.gdshader" "$PWD/source-assets/reflection51b/source-change-ledger.json" "$PWD/source-assets/reflection51b/shadow-guard-ledger.json" "$PWD/source-assets/reflection51b/build-scope.json" "$OUT/"
cp -r "$PWD/source-assets/reflection51b/guarded-shaders" "$OUT/"
sha256sum "$PROJECT/scenes/candidate51/Game51.tscn" "$PROJECT/scenes/candidate51/build-report-51.json" "$PROJECT/tools/build_lake_reflection51b.gd" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/assets/reflection51b/lake_water_reflection51b.gdshader" "$PWD/source-assets/reflection51b/source-change-ledger.json" "$PWD/source-assets/reflection51b/shadow-guard-ledger.json" "$PWD/source-assets/reflection51b/guarded-shaders/"*.gdshader > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/build_lake_reflection51b.gd -- --diagnostic-dir="$OUT" > "$OUT/build.stdout.log" 2> "$OUT/build.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/build.exit-code.txt"
cat "$OUT/build.stdout.log";cat "$OUT/build.stderr.log" >&2
printf 'Independent Game51b build exit %s; evidence %s; full verification pending\n' "$CODE" "$OUT"
exit "$CODE"
