#!/usr/bin/env bash
set -u
ROOT=/workspace/scratch/a29d03198654/Aether
RUN=$(mktemp -d "$ROOT/cloud-evidence/cirque54-world-diagnostic-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$RUN" > /workspace/scratch/a29d03198654/tools-feiting/cirque54-world-last.txt
export CIRQUE54_WORLD_OUT="$RUN/images"
mkdir -p "$CIRQUE54_WORLD_OUT"
sha256sum "$ROOT/source-assets/lake-cirque54/v1/diagnose_cirque54_world.gd" "$ROOT/source-assets/lake-cirque54/v1/cirque54-payload.json" "$ROOT"/source-assets/lake-cirque54/v1/*_cirque54.blend > "$RUN/input-sha256.txt"
cp "$ROOT/source-assets/lake-cirque54/v1/diagnose_cirque54_world.gd" "$RUN/diagnose_cirque54_world.gd"
export XDG_DATA_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/data"
export XDG_CACHE_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/cache"
export XDG_CONFIG_HOME="/workspace/scratch/a29d03198654/tools-feiting/userdata/config"
/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 --path "$ROOT/candidates/round40-exclusive-20260930/project" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --resolution 1280x960 --script "$ROOT/source-assets/lake-cirque54/v1/diagnose_cirque54_world.gd" -- "$@" > "$RUN/stdout.log" 2> "$RUN/stderr.log"
status=$?
printf '%s\n' "$status" > "$RUN/exit-code.txt"
printf '%s\n' "$RUN"
exit "$status"
