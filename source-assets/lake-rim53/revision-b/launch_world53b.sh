#!/usr/bin/env bash
set -u
ROOT=/workspace/scratch/a29d03198654/Aether
RUN=$(mktemp -d "$ROOT/cloud-evidence/rim53b-world-diagnostic-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$RUN" > /workspace/scratch/a29d03198654/tools-feiting/rim53b-world-last.txt
export RIM53_PREVIEW_OUT="$RUN/images"
mkdir -p "$RIM53_PREVIEW_OUT"
sha256sum "$ROOT/source-assets/lake-rim53/revision-b/diagnose_west53b_world.gd" "$ROOT/source-assets/lake-rim53/revision-b/rim53-payload.json" "$ROOT"/source-assets/lake-rim53/revision-b/*_rim53.blend > "$RUN/input-sha256.txt"
cp "$ROOT/source-assets/lake-rim53/revision-b/diagnose_west53b_world.gd" "$RUN/preview_sources53.gd"
export XDG_DATA_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/data"
export XDG_CACHE_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/cache"
export XDG_CONFIG_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/config"
/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 --path "$ROOT/candidates/round40-exclusive-20260930/project" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --resolution 1280x960 --script "$ROOT/source-assets/lake-rim53/revision-b/diagnose_west53b_world.gd" -- "$@" > "$RUN/stdout.log" 2> "$RUN/stderr.log"
status=$?
printf '%s\n' "$status" > "$RUN/exit-code.txt"
printf '%s\n' "$RUN"
exit "$status"
