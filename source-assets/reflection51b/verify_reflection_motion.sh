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
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51b-motion-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51b-motion-last.txt"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/verify_reflection51b_motion_only.gd" "$OUT/"
cp "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$OUT/"
cp "$PROJECT/assets/reflection51b/lake_water_reflection51b.gdshader" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/scenes/candidate51b/build-report-51b.json" "$OUT/"
sha256sum "$PROJECT/tools/verify_reflection51b_motion_only.gd" "$PROJECT/scenes/candidate50/Game50.tscn" "$PROJECT/scenes/candidate51/Game51.tscn" "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$PROJECT/assets/reflection51/lake_water_reflection51.gdshader" > "$OUT/input-sha256.txt"
cat > "$OUT/SCOPE.txt" <<'EOF'
Saved51b limited reflection/movement-only verification. Prior full1344 conversion gate remains false(two pixels, <=2channel units), as do inherited350m motion failures. Two-hop saved-state/material audit retained. Actual shared-world reflection, ship/camera translation, side/back images and restoration are independently recorded. No normal-pass rerun or threshold relaxation, no scene save. Totalvisual/reference/hardware acceptance remain false.
EOF
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_reflection51b_motion_only.gd -- --output-dir="$OUT/images" "${EXTRA[@]}" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log"; cat "$OUT/verify.stderr.log" >&2
printf 'Saved51b verification (%s) exit %s; evidence %s. No total acceptance claim.\n' "$MODE" "$CODE" "$OUT"
exit "$CODE"
