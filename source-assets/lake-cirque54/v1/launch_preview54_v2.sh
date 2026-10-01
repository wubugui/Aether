#!/usr/bin/env bash
set -u
ROOT=/workspace/scratch/a29d03198654/Aether
SOURCE="$ROOT/source-assets/lake-cirque54/v1"
RUN=$(mktemp -d "$ROOT/cloud-evidence/cirque54-source-preview-v2-$(date -u +%Y%m%dT%H%M%SZ)-XXXXXX")
printf '%s\n' "$RUN" > /workspace/scratch/a29d03198654/tools-feiting/cirque54-preview-last.txt
export CIRQUE54_PREVIEW_OUT="$RUN/images"
mkdir -p "$CIRQUE54_PREVIEW_OUT"
sha256sum "$SOURCE/preview_cirque54_framing_v2.gd" "$SOURCE/launch_preview54_v2.sh" "$SOURCE/cirque54-payload.json" "$SOURCE/massif_cirque_wall_cirque54.blend" "$SOURCE/native-readback-proof.json" "$SOURCE/continuous-footprint-proof.json" "$ROOT/candidates/round40-exclusive-20260930/project/scenes/candidate53d-west/Game53dWest.tscn" > "$RUN/input-sha256.txt"
cp "$SOURCE/preview_cirque54_framing_v2.gd" "$RUN/preview_cirque54_framing_v2.gd"
cp "$SOURCE/native-readback-proof.json" "$SOURCE/continuous-footprint-proof.json" "$RUN/"
export XDG_DATA_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/data
export XDG_CACHE_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/cache
export XDG_CONFIG_HOME=/workspace/scratch/a29d03198654/tools-feiting/userdata/config
/workspace/scratch/a29d03198654/tools-feiting/Godot_v4.5.1-stable_linux.x86_64 --path "$ROOT/candidates/round40-exclusive-20260930/project" --rendering-method gl_compatibility --audio-driver Dummy --disable-vsync --resolution 1280x960 --script "$SOURCE/preview_cirque54_framing_v2.gd" > "$RUN/stdout.log" 2> "$RUN/stderr.log"
status=$?
printf '%s\n' "$status" > "$RUN/exit-code.txt"
printf '%s\n' "$RUN"
exit "$status"
