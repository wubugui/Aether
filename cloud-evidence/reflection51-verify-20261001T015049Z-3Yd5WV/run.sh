#!/usr/bin/env bash
set -euo pipefail
R=/workspace/scratch/a29d03198654
P="$R/Aether/candidates/round40-exclusive-20260930/project"
OUT=$(mktemp -d "$R/Aether/cloud-evidence/reflection51-verify-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
echo "$OUT" > "$R/tools-feiting/feiting51-verify-last.txt"
export XDG_CACHE_HOME="$R/tools-feiting/userdata/cache" XDG_DATA_HOME="$R/tools-feiting/userdata/data" XDG_CONFIG_HOME="$R/tools-feiting/userdata/config"
cp "$P/tools/verify_lake_reflection51.gd" "$P/tools/build_lake_reflection51.gd" "$P/tools/reflection51_materials.gd" "$P/scripts/lake_reflection51.gd" "$OUT/"
sha256sum "$P/scenes/candidate50/Game50.tscn" "$P/scenes/candidate51/Game51.tscn" "$P/tools/verify_lake_reflection51.gd" "$P/scripts/lake_reflection51.gd" "$P/assets/reflection51/"*.tres > "$OUT/input-sha256.txt"
cp "$(readlink -f "${BASH_SOURCE[0]}")" "$OUT/run.sh"
set +e
"$R/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$P" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_lake_reflection51.gd -- --output-dir="$OUT/images" > "$OUT/stdout.log" 2> "$OUT/stderr.log"
CODE=$?
echo "$CODE" > "$OUT/exit-code.txt"
printf 'Full51 verifier exit %s, evidence %s\n' "$CODE" "$OUT"
exit "$CODE"
