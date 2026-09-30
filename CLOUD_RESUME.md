# Cloud continuation — 2026-09-30 UTC

Read unchanged GOAL.md first: all 20 reference images plus the original opening in one real 3D world. All visual acceptance remains pending. Do not confuse functional checks, migration, source asset review or software-rendered pixels with complete GPU/visual acceptance.

## Repository state

- Working branch: development/feiting-cloud-20260930. Never write/force-push the migration branch.
- Original cloud baseline: 98486d31c6769b2a572e5d9f4a7a6754922b0e46.
- Completed migration 851f7374f1f9625c57aa1c992f4550efaa8e6bee was merged normally as a005f961390750067f68a3ee8b29e7f1a0f47056. It added historical captures/Blender sources/delivery records and changed only MIGRATION_HANDOFF.md among existing paths; active candidate unchanged.
- Sparse checkout intentionally avoids expanding all historical capture files. Do not run unbounded blob-reading commands on the full partial-clone tree merely to produce statistics.
- Active project: candidates/round40-exclusive-20260930/project. Its default still Game42c, not a claim that later candidates are rejected for all purposes. New candidates are explicitly loaded by verification tools.
- Protected cliff master remains unchanged: SHA256 abb66e414168cbd24e2495b64c27714759c844ff75582b0f71d5384d8f760dd7.

## Tools and actual rendering

Official Godot 4.5.1 stable is installed in /workspace/shared/feiting-tools/Godot_v4.5.1-stable_linux.x86_64. Official Blender 4.5.14 LTS in /workspace/shared/feiting-tools/blender-4.5.14-linux-x64/blender was checksum-verified. User explicitly permitted cloud Blender on September 30, overriding the previous Hub-only restriction. Do not modify either user's network settings.

Cloud desktop X11 can run Godot Compatibility, but reports Mesa llvmpipe software rendering. No hardware GPU gate is satisfied. Cloud shell does not expose the display; run graphical commands through the existing cloud desktop terminal. Use isolated XDG directories and Dummy audio. The VSync unsupported warning is known and retained, never suppress other warnings/errors.

Important Godot lifecycle fix: an off-tree Sky released before the renderer updates leaks two 349,524-byte textures. A minimal immediate-vs-settled reproduction proves this. After each instantiate, including CACHE_MODE_IGNORE reload, wait at least 3 process frames plus frame_post_draw before freeing. Wait 8 frames after cleanup. Never save the whole gameplay scene after adding it to the live tree merely to avoid this error, since ready changes state.

## Candidates and evidence

### 42d — persistent rain/snow instance fix

Commit e6d6cb37597b2eb596649da6f2ca03675d0d3fb7. Scene SHA256 5742de44e7f44070ca7475e801ea82b4f9be6433b8a1cef55e00aa667f1607e9.

42b/42c had no saved rain/snow buffers. 42d explicitly allocates/copies and reconstructs the exact original seeded payload and placement. 100 allocation checks pass. All 48,000 buffer floats survive reload. Native scene geometry/collision/structure of 10,446 other nodes is equivalent; 1,524 null shader parameters were explicitly serialized as their declared defaults.

Initial build run stays failed because it emitted the Sky cleanup errors. Do not rewrite it as passed. Separate delayed reload and actual-tree smoke recover this exact saved scene without rebuilding. Smoke: 17/17 checks, 12 raw images, exit 0, no texture leak, software renderer. Rain/snow move and are visible but far too sparse for storm/blizzard reference fidelity. 1341 initial differential was contaminated by lightning settling; use the explicit off/restored independent report instead. Details: cloud-evidence/multimesh42d-diagnosis-20260930-1914/recovery-report.json.

### 43 — upper-cloud volume comparison

Commit abafd821dd58c09c44506997ae317deb76ccd846. Scene SHA256 a3a741df4fb4f19bd397e26050cd4854bb9e5b6d4344d8af0dbf1bc45322dc95.

Replaces only 12 upper-cloud groups with retained upper43 editable source. Build/reload preservation passed without ERROR. Focused 54 checks/26 actual software-rendered images passed; all visual acceptance pending. CPU source preview has real rounded undersides, but actual night views still read as rock/ball clusters. Cloud-sea floor still has coarse rock-like facets. Diag-only hiding of DistantCloudBank41 removes the original large opening-view gray ceiling, confirming exact source; these hidden-group images are not production beauty evidence.

### 44 — distant-cloud bank geometry

Saved scene SHA256 e679ad1510b8e222b83194534f58752a6f40edc8eb0e1c4a128c042af1feb347. Build/reload preservation passed. Focused software-renderer run completed 117 limited checks and 32 images with exit 0 and no ERROR, retaining the known VSync warning. Independent visual review rejects it as a finished match. Check /workspace/shared/feiting44-last-run.txt for exact evidence.

New editable source-assets/cloud-bank44 retains three variants, each 21 closed pieces/2,400 triangles. Only the 56 original distant bank meshes were replaced; original names, transforms and variation mapping preserved. Opening 1343 and 1128 frontal sky opens substantially. This does not mean all gray ceiling is gone: side/back retain thick gray clouds, and high-altitude perimeter can be too sparse. Independent review is cloud-evidence/cloud44-independent-review.md when complete. The 1128 translated camera enters terrain; preserve that failed observation, do not count it as valid flight evidence.

### 45 — material-only study under preparation

Only a future isolated native Lambert Wrap material comparison is being prepared. It must preserve geometry, cameras, sun/environment, native source files, colors and all non-diffuse material properties. No emission/unshaded or full-screen disguise. Do not state it exists or works before actual build and pixels.

## Publication boundary

Cloud has public repository read but lacks Git shell write authentication. No token was copied or requested. A verified incremental git bundle can be materialized through authorized Library transfer into the existing authenticated migration executor only to import and normally push the independent cloud branch; this does not resume local development. Remote publication must be read back before claiming push success. Tool binaries, personal configuration, credentials and signed upload URLs stay excluded.
