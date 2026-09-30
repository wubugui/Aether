# Aether local-to-cloud handoff — 2026-09-30

Local development stopped at the user's instruction. This branch preserves project material; migration is not GOAL acceptance. Read the unchanged `GOAL.md` for the full requirement.

## Current candidate and evidence

The unique latest implemented candidate is `candidates/round40-exclusive-20260930/project`, default scene `res://scenes/candidate42c/Game42c.tscn`. Scene SHA256: `06f86e4bc73ed2d28a4eb6d76e89e3946cb6b6c6e7e72b9b36f55ed972880c91`.

Game42c: `evidence/gpu-i-particle42c-1757` contains 36 actual GPU captures and 105/105 limited functional checks. Runtime stderr was empty. Its build still has two real MultiMesh buffer errors (`build-42c-1754.stderr.log`). Rain/snow visibility is not established; do not count functional checks as visual acceptance. No Game43 scene was built. Previously submitted upper43 Hub task completed; five outputs were downloaded and SHA256 verified after the stop instruction, without a new submission. Editable source is `source-assets/hub-upper43/upper_cloud43.blend`.

History: Game40c had 58/58 limited checks and 15 captures (`gpu-d-resume1629`); Game41 had 61/61 and 16 (`gpu-e-cloud41`); Game41b had 62/62 and 16 (`gpu-f-cloud41b-1712`), plus a real normal startup check; Game42b had 105/105 and 36 (`gpu-g-weather42b-1733`). These are historical evidence, not a regression or repeated job. The legacy `run-candidate40.cmd` still opens Game41b; use the command below for the latest candidate.

All 20 reference scenes plus the original reference remain visually unaccepted. Major remaining differences include cloud undersides, terrain/port composition, mountain and water detail, weather presence, spatial lighting, and cabin furnishings. Preserve failed screenshots and original standards.

## Resume on cloud

Install Godot **4.5.1 stable**, with a real GPU supporting the Compatibility renderer; the local evidence used a GTX970 and OpenGL 3.3. Import caches are deliberately omitted. Run:

```sh
godot --editor --path candidates/round40-exclusive-20260930/project
godot --path candidates/round40-exclusive-20260930/project
godot --path candidates/round40-exclusive-20260930/project --script res://tools/verify_weather42c.gd -- --output-dir=/absolute/new/output/path
```

Use a unique output directory and isolate Godot user data. Import the project before runtime or verification on a clean machine. Do not overwrite old evidence. Verification requires actual GPU rendering; headless parsing is insufficient. Windows runners hardcode the old local `.tools/godot` path and need the installed executable substituted on the cloud machine. Python 3.10+ and `requests`/`Pillow` support existing Hub and report utilities. Blender 4.5 editable files are retained; do not regenerate protected `blender/cliff_kit/cliff_eastern_plateau.blend`. The prior Inference Hub was a LAN service and may be unavailable from the cloud; arrange normal authorized access or use retained native outputs. No credentials are included.

First fix the MultiMesh allocation problem and establish visible, moving rain/snow, then use the saved independent upper43 cloud assets. These are continuation recommendations, not changes performed after the stop instruction. The shared root project is preserved separately from the exclusive candidate; no uncertain shared changes were overwritten or merged.

## Transfer inventory

Final delivery manifests enumerate included files with SHA256 and excluded files with reasons. Original source material, editable native assets, candidate versions, scripts, actual screenshots and reports are preserved. Third-party executables/runtimes, Godot/import caches, personal session history/configuration, credentials, and redundant packaged archives are omitted. Excluded originals remain untouched locally. The target repository was verified public and empty before migration. A separate `migration/feiting-20260930` branch is used; no force push or default-branch replacement is authorized.
