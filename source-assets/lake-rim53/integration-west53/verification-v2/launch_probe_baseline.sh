#!/usr/bin/env bash
set -u
ROOT=/workspace/scratch/a29d03198654/Aether
PREP="$ROOT/source-assets/lake-rim53/integration-west53"
RUN=$(mktemp -d "$ROOT/cloud-evidence/rim53d-full-baseline-probes-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$RUN" > /workspace/scratch/a29d03198654/tools-feiting/rim53d-full-baseline-probes-last.txt
sha256sum "$PREP/verification-v2/probe_full_baseline.gd" "$PREP/runtime-probes.json" "$ROOT/candidates/round40-exclusive-20260930/project/scenes/candidate51b/Game51b.tscn" > "$RUN/input-sha256.txt"
cp "$PREP/verification-v2/probe_full_baseline.gd" "$RUN/"
export XDG_DATA_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/data
export XDG_CACHE_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/cache
export XDG_CONFIG_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/config
/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 --path "$ROOT/candidates/round40-exclusive-20260930/project" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --resolution 1180x664 --script "$PREP/verification-v2/probe_full_baseline.gd" -- --report-dir="$RUN" > "$RUN/stdout.log" 2> "$RUN/stderr.log"
status=$?
printf '%s\n' "$status" > "$RUN/exit-code.txt"
printf '%s\n' "$RUN"
exit "$status"
