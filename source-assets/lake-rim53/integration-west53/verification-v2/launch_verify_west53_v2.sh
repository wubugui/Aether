#!/usr/bin/env bash
set -u
ROOT=/workspace/scratch/a29d03198654/Aether
PREP="$ROOT/source-assets/lake-rim53/integration-west53"
BASELINE_REPORT="/workspace/scratch/a29d03198654/Aether/cloud-evidence/rim53d-full-baseline-probes-20261001T064320Z-3Zwd4U/full-baseline-building-probes.json"
RUN=$(mktemp -d "$ROOT/cloud-evidence/rim53d-west-verify-v2-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$RUN" > /workspace/scratch/a29d03198654/tools-feiting/rim53d-west-verify-v2-last.txt
sha256sum "$BASELINE_REPORT" "$PREP/verification-v2/baseline-proof-binding.json" "$PREP/verification-v2/verify_west53_v2.gd" "$PREP/build_west53.gd" "$PREP/west53_audit.gd" "$PREP/integration-manifest.json" "$PREP/integration-payload.json" "$PREP/runtime-probes.json" "$ROOT/candidates/round40-exclusive-20260930/project/scenes/candidate53d-west/Game53dWest.tscn" "$ROOT/candidates/round40-exclusive-20260930/project/scenes/candidate53d-west/build-report-west53.json" > "$RUN/input-sha256.txt"
cp "$PREP/verification-v2/baseline-proof-binding.json" "$PREP/verification-v2/verify_west53_v2.gd" "$PREP/west53_audit.gd" "$RUN/"
export XDG_DATA_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/data
export XDG_CACHE_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/cache
export XDG_CONFIG_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/config
/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 --path "$ROOT/candidates/round40-exclusive-20260930/project" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --resolution 1180x664 --script "$PREP/verification-v2/verify_west53_v2.gd" -- --report-dir="$RUN" --baseline-probes="$BASELINE_REPORT" "$@" > "$RUN/stdout.log" 2> "$RUN/stderr.log"
status=$?
printf '%s\n' "$status" > "$RUN/exit-code.txt"
printf '%s\n' "$RUN"
exit "$status"
