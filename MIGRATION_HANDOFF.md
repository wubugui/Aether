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

All 10 material batches were successfully pushed. `delivery/file-manifest.json` enumerates 46,357 retained original files with SHA256; `delivery/integrity-result.json` records zero original-byte or committed-blob mismatches and a passing full Git fsck. All 32 project input/evidence ZIP archives were content-audited and preserved as well. Original source material, editable native assets, candidate versions, scripts, actual screenshots and reports are retained.

`delivery/excluded-files.json` and `delivery/cache-exclusions.json` enumerate exclusions, summarized in `delivery/exclusion-summary.json`: third-party executables/runtimes, Godot/Python/import caches, personal session history/configuration and previous machine inventories, private app-server administration records, and reproducible executable exports. Older Windows `.exe`/`.pck` builds are omitted as reproducible exports and are not the latest Game42c candidate; use the preserved native candidate with Godot. All excluded originals remain untouched locally. No native project resource or acceptance screenshot was excluded to fit the receiving disk.

The source inventory covers 251,974 files / 23,573,353,639 bytes. Retained originals materialize to 14,934,413,206 bytes; exact SHA256 unique contents total 6,248,585,590 bytes, with 58.16% byte-identical repetition. The full local Git database measured 2,298,033,096 bytes before this final metadata commit; normal packed clone storage can differ. The candidate directory materializes to 1,270,436,095 bytes; 1.23% is byte-identical repetition within that directory. Similar but differing native scene revisions are separately preserved and may compress further with Git delta packing. See `delivery/storage.json` and `delivery/native-inventory.json`.

The public target repository was empty before migration. The initial migration branch became the default automatically on first push; no existing history was replaced and no force push was used. Cloud development should use a separate work branch. `delivery/remote-keyfiles.json` records an independent remote clone and successful byte-level roundtrip of GOAL, latest scene/config/code, actual screenshot and protected Blender mother.

The receiving cloud machine has about 30GB free, shared with another project. Do not require a full materialized historical checkout. Ordinary Git deduplicates identical blobs; there is no Git LFS dependency or upload. For the latest candidate, references, review records and protected editable cliff kit:

```sh
git clone --filter=blob:none --no-checkout --single-branch --branch migration/feiting-20260930 https://github.com/wubugui/Aether.git
cd Aether
git sparse-checkout init --cone
git sparse-checkout set candidates/round40-exclusive-20260930 ref reviews blender/cliff_kit
git checkout migration/feiting-20260930
```

Root documentation is included in cone mode. Add historical directories only when needed, for example `git sparse-checkout add captures/validation_runs`, `captures/asset_backups`, `captures/edit_backups`, `captures/acceptance39`, `MIGRATION_20260906/attachments`, or another `blender` kit. All accepted paths remain in Git and the manifests; sparse checkout omits them only from the local working tree. Final exact unique-content and .git byte measurements are in the delivery records.
