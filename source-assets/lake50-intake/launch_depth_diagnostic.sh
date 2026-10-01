#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
OUT=$(mktemp -d "$PWD/cloud-evidence/depth50-control-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting50depth-last.txt"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
DIAG="$PWD/cloud-evidence/reflection50-material-intake/diagnose_water_depth50.gd"
HEIGHT="$PWD/source-assets/lake50-intake/height49-1m-rf.res"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$DIAG" "$OUT/"
sha256sum "$PROJECT/scenes/candidate49/Game49.tscn" "$HEIGHT" "$DIAG" > "$OUT/input-sha256.txt"
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script "$DIAG" -- --height-texture="$HEIGHT" --output-dir="$OUT/images" > "$OUT/diagnostic.stdout.log" 2> "$OUT/diagnostic.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/diagnostic.exit-code.txt"
cat "$OUT/diagnostic.stdout.log";cat "$OUT/diagnostic.stderr.log" >&2
printf 'Read-only depth causal diagnostic exit %s; evidence %s; no candidate saved\n' "$CODE" "$OUT"
exit "$CODE"
