#!/usr/bin/env bash
set -euo pipefail
SCRIPT_PATH=$(readlink -f "${BASH_SOURCE[0]}")
ROOT=/workspace/scratch/a29d03198654
cd "$ROOT/Aether"
export XDG_CACHE_HOME="$ROOT/tools-feiting/userdata/cache"
export XDG_DATA_HOME="$ROOT/tools-feiting/userdata/data"
export XDG_CONFIG_HOME="$ROOT/tools-feiting/userdata/config"
PROJECT="$PWD/candidates/round40-exclusive-20260930/project"
MODE=full
EXTRA=()
if [[ "${1:-}" == "--normal-only" ]]; then MODE=normal; EXTRA+=(--normal-only); fi
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51-verify-v2-${MODE}-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51-verify-v2-last.txt"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$OUT/"
cp "$PROJECT/assets/reflection51/lake_water_reflection51.gdshader" "$OUT/"
sha256sum "$PROJECT/scenes/candidate50/Game50.tscn" "$PROJECT/scenes/candidate51/Game51.tscn" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$PROJECT/assets/reflection51/lake_water_reflection51.gdshader" > "$OUT/input-sha256.txt"
cat > "$OUT/SCOPE.txt" <<'EOF'
Saved51off v2 verifier only. Original v1 and failed evidence remain unchanged. Every reference records original-vs-converted and original-vs-copy differences without tolerance. The authorized mandatory full RGBA zero-diff gate is all114 same-value original material copies plus Ocean versus converted resources, followed by original A/A2 restoration and clip-only main/shadow zero-diff. Clone Shader objects/code remain original. Full mode covers seven references/weather states, then two clear reflection views and controlled existing-ship/camera motion. Dynamic waterline-straddling clipping, arbitrary future streamed-instance coverage, hardware-GPU and full-world visual acceptance remain unproven. Original resource 5px identity effect is not called zero-diff. Inherited350m failures remain failures. Known51 reflection-edge artifacts remain. Exit0 indicates only scoped copy-baseline/runtime gates, never total acceptance.
EOF
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_lake_reflection51_v2.gd -- --output-dir="$OUT/images" "${EXTRA[@]}" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log"; cat "$OUT/verify.stderr.log" >&2
printf 'Saved51 v2 verification (%s) exit %s; evidence %s. No total acceptance claim.\n' "$MODE" "$CODE" "$OUT"
exit "$CODE"
