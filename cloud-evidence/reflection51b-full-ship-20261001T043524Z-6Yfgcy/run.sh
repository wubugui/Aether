#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51b-full-ship-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51b-full-ship-last.txt"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/observe_full_ship_reflection51b.gd" "$OUT/"
sha256sum "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/tools/observe_full_ship_reflection51b.gd" "$PROJECT/scripts/lake_reflection51b.gd" "$PWD/cloud-evidence/reflection51b-motion-20261001T041545Z-WCymsr/images/reflection-motion-report.json" > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/observe_full_ship_reflection51b.gd -- --output-dir="$OUT/images" > "$OUT/stdout.log" 2> "$OUT/stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/exit-code.txt"
cat "$OUT/stdout.log"
cat "$OUT/stderr.log" >&2
exit "$CODE"
