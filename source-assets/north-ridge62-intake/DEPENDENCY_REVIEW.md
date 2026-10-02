# Game61 dependency-loading review, frozen 2026-10-02

## Result and immediate consequence

The current inspected dependency closure exposes no project-code load-time execution trigger:23 GDScripts have no static variables, `_static_init` or `_init`; their resolved native bases are Node/Node3D/Control variants or RefCounted, not Resource. All1543 serialized `script` properties inspected in1301 binary resource files are null. Text resource script attachments are absent;1313 text script assignments belong to scene nodes. The5 actual compressed imported prefab scenes contain only native materials, meshes and PackedScene resources, with no external dependencies or script-bearing resources.

This is a bounded source-and-serialization result. `ResourceLoader.load` is not inherently free of script execution. No Godot/Blender process, native GDScript parsing, scene instantiation, world execution or rendering was performed here. Native work, allocations, cache activity and diagnostics are not ruled out by absence of project GDScript callbacks.

**The existing1477-input manifest omits51 files in the actual dependency closure, including9 GDScripts and5 imported scene caches.** The new review records their exact identities; it does not change the published runner or any historical test. Before later parsing/collection, the caller should add this explicit delta and startup controls to its own input identity check. Existing1477 results remain statements about their original recorded set, not retrospectively rewritten full-dependency claims.

## Entry and complete reviewed set

Entry: `res://scenes/candidate61-coast/Game61Coast.tscn`, SHA256 `dff06de665e1fa1f6ab74ff3cdf4e91442e1ac322839a37718e799f0d7fa44d8`.

Saved scene inheritance is61→60→56→55→53d. The53d source loads five vegetation prefab scenes in addition to the native resource graph. The review contains1483 current files and2304 dependency edges, including all literal script inheritance/preload dependencies. Preloads inside ordinary functions are included because compilation still resolves them; their enclosing `.new()`, `snapshot()` and lifecycle bodies were not invoked.

`DEPENDENCY_REVIEW.json` contains:

- `files`: the entire reviewed set, per-file SHA256, byte length and kind; binary rows also record class, null-script count and successful property-stream boundary validation
- `dependencies_by_parent`: actual loading edges, including external tables, prefab/import remaps, script inheritance and preload line numbers
- `script_loading_paths_and_sha256`: all23 scripts, SHA, incoming paths, native base and initialization declarations
- `prior_manifest_coverage_gap.not_covered`: the exact51-file set difference from the old1477 manifest, whose identity is also recorded
- `compressed_import_scenes`: all5 real cache paths, compressed/decompressed SHA, native types and import settings
- `startup_and_remap_controls`: actual settings/cache identities and relevant absent files
- `published_preparation_files_unchanged`: the6 pre-existing preparation artifacts, frozen without modification
- `audit_method`: source-reading scope and the temporary Python auditors used for reproducibility; no geometry/scatter payloads are included

All1483 source identities were rechecked after the read pass with no changes. The original5 source/plan hashes still match PREPARATION_CHECK; that check file itself is also preserved. The parent identified the prior publication as27894128; this worker made no Git calls and does not claim independent remote verification.

## Script-loading paths

- Root: Game60Observation.gd→game55_observation.gd→game42b.gd→game.gd→Node3D
- World: world39.gd→open_world.gd→Node3D; open_world preloads world_math.gd, native world/terrain/cloud materials and water shader
- Weather: weather42c.gd→weather42b.gd→Node3D
- The53d scene directly binds airship_body, asset_instance, scatter_group, world_port, lake_depth50, lake_reflection51b and environment42b as node scripts
- game.gd preloads game_hud→hud, game_tests, flight_tour_test, stream_flight_test and cliff_tour_test; the test helpers preload validation_context
- airship_body preloads native ship/flag materials; environment42b preloads a shader

The9 scripts absent from the prior manifest are weather42b.gd, game_hud.gd, game_tests.gd, flight_tour_test.gd, stream_flight_test.gd, cliff_tour_test.gd, world_math.gd, hud.gd and validation_context.gd. Their full res:// paths, exact SHA and loading edges are in the JSON. The old manifest's19 GDScript paths and this closure's23 are different sets, not simply four newly found scripts.

Seven reviewed scripts have `@tool`; that annotation alone is not evidence of automatic execution. The only observed static functions are scatter_group.copy_data and validation_context.snapshot. They are ordinary callable helpers, not static constructors. Neither has an automatic load-time call path in the inspected sources.

## Resource and remap audit

The1301 binary files include1296 ordinary RSRC resources and5 small RSCC mode2 imported scenes. A bounded Python decoder follows the official4.5.1 metadata and Variant formats. It reads resource/property structure, skips packed geometry/image/scatter payloads, and verifies every internal resource's end offset plus the file trailer. All1301 streams parsed, with no unknown types, nonnull script fields or legacy inline external-resource references. The first header-only pass found the word `script` in resource string tables; the full property pass established their actual1543 values are null, rather than treating a string-table name as an attached script.

The compressed files total only native poplar/oak/rock/bush/pine prefab caches. Existing installed zstandard was used; no tool/package was downloaded. Each decompressed resource has0 external dependencies and the same native type pattern: StandardMaterial3D, two ArrayMesh resources and PackedScene. Their `.glb.import` files set `nodes/root_script=null` and `import_script/path=""`. The actual cached bytes were inspected; clean importer settings alone were not used as proof.

Every inspected external-resource UID declaration is absent/invalid, so this closure does not take the valid-UID-overrides-path branch. The UID cache still has a recorded SHA. No per-dependency `.remap` files or project translation/resource-remap settings were found. The global script-class cache is exactly `list=[]`; extension_list.cfg and override.cfg are absent; project.godot has no autoload. Its editor plugin setting does not run under the planned non-editor command. These facts concern the current files and must be rechecked if settings/cache state changes.

## Why this audit was necessary

Godot4.5.1 can run static variable initializers and `_static_init` when a GDScript is compiled/loaded, without scene instantiation. See [reload execution](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/gdscript/gdscript.cpp#L759-L835) and [static initialization order](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/gdscript/gdscript_compiler.cpp#L2397-L2433). Preload contributes to the compilation dependency closure: [analyzer branch](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/gdscript/gdscript_analyzer.cpp#L4362-L4420).

Restoring a custom Resource's script can create its script instance and run member initialization/constructors, followed by property setters/getters. See [Object::set_script](https://github.com/godotengine/godot/blob/4.5.1-stable/core/object/object.cpp#L940-L964) and [instance initialization](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/gdscript/gdscript.cpp#L126-L188). That is why actual non-node script attachments were checked instead of relying on the collector's missing `.instantiate()` call.

Valid resource UIDs can replace textual paths: [text loader](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/resource_format_text.cpp#L401-L431). The binary audit follows [the versioned format](https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/resource_format_binary.cpp#L41-L97), [Variant decoder](https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/resource_format_binary.cpp#L166-L643) and [compressed-block layout](https://github.com/godotengine/godot/blob/4.5.1-stable/core/io/file_access_compressed.cpp#L38-L71).

## Remaining limits and next step

The concrete open issue is identity coverage: add the51 explicit files and relevant startup/cache checks to the next runner revision, then let the parent schedule native parse and collection. No user engineering-approval request is implied. Do not patch old manifests or relabel old tests. Keep this report and the already published preparation sources frozen.

Native parsing, saved-data collection, exact northern12-house membership, MultiMesh placement and runtime-generated geometry remain untested. No visual, collision, world or GOAL acceptance follows from this dependency review. A different engine, regenerated imported cache, changed script/UID mapping, new startup extension or scene-instantiating collector invalidates the corresponding assumptions.

## Lossless storage

The complete JSON is730050 bytes, SHA256 `4aa3634f3ec1d1e380d53d724ffa707af4bf66b7136c0bd5fc9592d4d9e80601`. `DEPENDENCY_REVIEW.json.gz` is a deterministic lossless copy; decompression was checked byte-for-byte against the original. Either representation preserves the complete set and code evidence; no truncation or summary substitutes for it.
