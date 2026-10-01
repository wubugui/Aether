#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$PWD/cloud-evidence/depth50-verify-v2-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting50-verify-last.txt"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/verify_lake_depth50_v2.gd" "$PROJECT/tools/build_lake_depth50.gd" "$PROJECT/scripts/lake_depth50.gd" "$OUT/"
sha256sum "$PROJECT/scenes/candidate49/Game49.tscn" "$PROJECT/scenes/candidate50/Game50.tscn" "$PROJECT/tools/verify_lake_depth50_v2.gd" "$PROJECT/tools/build_lake_depth50.gd" "$PROJECT/scripts/lake_depth50.gd" > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_lake_depth50_v2.gd -- --output-dir="$OUT/images" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log";cat "$OUT/verify.stderr.log" >&2
printf 'Saved Game50 verifier-v2 exit %s; evidence %s; no rebuild, no total acceptance claim\n' "$CODE" "$OUT"
exit "$CODE"
