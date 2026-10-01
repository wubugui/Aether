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
OUT=$(mktemp -d "$PWD/cloud-evidence/reflection51b-verify-${MODE}-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$OUT" | tee "$ROOT/tools-feiting/feiting51b-verify-last.txt"
cp "$SCRIPT_PATH" "$OUT/run.sh"
cp "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$OUT/"
cp "$PROJECT/assets/reflection51b/lake_water_reflection51b.gdshader" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/scenes/candidate51b/build-report-51b.json" "$OUT/"
sha256sum "$PROJECT/scenes/candidate50/Game50.tscn" "$PROJECT/scenes/candidate51/Game51.tscn" "$PROJECT/scenes/candidate51b/Game51b.tscn" "$PROJECT/tools/verify_lake_reflection51b.gd" "$PROJECT/tools/reflection51b_saved_audit.gd" "$PROJECT/scripts/lake_reflection51b.gd" "$PROJECT/tools/verify_lake_reflection51_v2.gd" "$PROJECT/tools/verify_lake_reflection51.gd" "$PROJECT/tools/build_lake_reflection51.gd" "$PROJECT/tools/reflection51_materials.gd" "$PROJECT/scripts/lake_reflection51.gd" "$PROJECT/assets/reflection51/lake_water_reflection51.gdshader" > "$OUT/input-sha256.txt"
cat > "$OUT/SCOPE.txt" <<'EOF'
Saved51b verifier only. No build or asset modification. Two-hop provenance: strict51-to51b full graph audit outside exact248 binding fields and5controller fields; all11450 original material fingerprints retained via51 ledger and51b mappings.12oldShader resource aliases remain12newShader resources with11unique guarded code bodies. All original material copies for pixel control are50 originals, not converted51. Every reference records original-vs-converted and original-vs-copy differences without tolerance. Required fullRGBA zero-diff gate is all114same-value original material copies plus Ocean versus51b converted resources, followed by originalA/A2 and clip-only main/shadow zero-diff. Full mode covers7reference/weather states then2clear reflection views and controlled existing-ship/camera motion. Dynamic waterline-straddling clipping, arbitrary future streams, hardware and full-world visual acceptance remain unproven. Inherited350m failures remain failures. Exit0 only acknowledges scoped copy-baseline/runtime gates, never totalacceptance.
EOF
set +e
"$ROOT/tools-feiting/Godot_v4.5.1-stable_linux.x86_64" --path "$PROJECT" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --script res://tools/verify_lake_reflection51b.gd -- --output-dir="$OUT/images" "${EXTRA[@]}" > "$OUT/verify.stdout.log" 2> "$OUT/verify.stderr.log"
CODE=$?
printf '%s\n' "$CODE" > "$OUT/verify.exit-code.txt"
cat "$OUT/verify.stdout.log"; cat "$OUT/verify.stderr.log" >&2
printf 'Saved51b verification (%s) exit %s; evidence %s. No total acceptance claim.\n' "$MODE" "$CODE" "$OUT"
exit "$CODE"
