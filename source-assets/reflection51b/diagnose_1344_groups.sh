#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51b-1344-groups-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51b-1344-groups-last.txt"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/diagnose_reflection51b_1344_groups.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$OUT/"
sha256sum "$PROJECT/scenes/candidate50/Game50.tscn" "$PROJECT/scenes/candidate51/Game51.tscn" "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/tools/diagnose_reflection51b_1344_groups.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/tools/build_lake_reflection51.gd" > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/diagnose_reflection51b_1344_groups.gd -- --output-dir="$OUT/images" > "$OUT/stdout.log" 2> "$OUT/stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/exit-code.txt"
cat "$OUT/stdout.log";cat "$OUT/stderr.log" >&2
printf 'Reflection51 material bisection exit%s, %s. Diagnostic only, all saved scenes untouched.\n' "$CODE" "$OUT"
exit "$CODE"
