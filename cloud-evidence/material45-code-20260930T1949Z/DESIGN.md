# Candidate45: single-variable native cloud-material experiment

Status: code and Godot 4.5.1 static parsing only. No build, scene serialization, GUI execution, captures, visual acceptance, or hardware GPU acceptance performed here. `scenes/candidate45/` is deliberately empty until separately authorized runtime execution.

## Inspected evidence and hypothesis

Inspected actual 44 `distant44-all-reference-1343.png` and `-side.png`, 43 `upper43-all-reference-1216-side.png`, and original `ref/1343.png`. The 44 clouds have hard white lit crowns and blue-gray planar undersides; 43's moonlit cloud sea reads like rock. Lambert Wrap may soften the terminator by extending native diffuse response beyond 90 degrees with roughness=1. This is a testable hypothesis, not a claimed visual improvement. It cannot repair crowded silhouettes, separated puff geometry, sparse distant banks, or black geometric gaps.

Official Godot 4.5 source: https://docs.godotengine.org/en/4.5/tutorials/3d/standard_material_3d.html#diffuse-mode describes Lambert Wrap as roughness-dependent and energy-conserving. Native StandardMaterial3D was deliberately retained; no unshaded, emission, custom screen shader, new textures, environment changes, or geometry changes.

## Scope and preflight

Base scene SHA256: e679ad1510b8e222b83194534f58752a6f40edc8eb0e1c4a128c042af1feb347

`static-material-inventory.json` records actual serialized 44 resources: 1808 single-surface MeshInstance3D nodes under the three authorized prefixes (CloudSea 500, UpperCloudBank43 132, DistantCloudBank41 1176). All use one of nine StandardMaterial3D resources with vertex colors as albedo and implicit native roughness=1. Runtime asserts enforce type, roughness, shaded/no-emission status, expected inventory and DIFFUSE_LAMBERT_WRAP==2.

The builder duplicates each source material once into a cache. Existing mesh-wide material_override remains mesh-wide; otherwise a per-surface override is set using each surface's actual active material. Mesh surface materials are never mutated. This remains safe if multiple surfaces are introduced, but changed total counts deliberately require review.

Full-world fingerprint visits every node, including targets, and every stored node/resource property recursively. Only target override slots and target active diffuse_mode are excluded from preservation comparison. Mesh resources and their surface payload/material resources, collision resources, local transforms, scripts, lights, environment, camera and explicit exact MultiMesh buffers/config are included. Target active materials are compared property-by-property with only diffuse_mode omitted; expected final wrapped material properties are compared after reload. Root owner and scene_file_path are excluded because scene flattening changes serialization ownership. Before/after/reload equality and unchanged 44 scene SHA are mandatory. No base resource is saved.

Each off-tree instantiated scene survives at least 3 process frames plus frame_post_draw before it can be freed. After scene cleanup, eight process frames precede exit.

## Runtime plan, not executed

Use an actual renderer, separate new output directories and isolated Godot user data. Both scripts reject headless execution. `--headless --check-only` was used solely for parser checks.

1. Execute `--script res://tools/build_cloud_material45.gd` in the existing candidate project.
2. Run `--script res://tools/verify_cloud_material45.gd -- --baseline --output-dir=<new44dir>`.
3. Run `--script res://tools/verify_cloud_material45.gd -- --output-dir=<new45dir>`.
4. Independently inspect paired actual images before drawing any material conclusion. Hardware GPU acceptance remains unavailable and false when these runs use llvmpipe.

Verifier uses the original reference positions. It captures 1343/1128/1216 front, 55-degree side, 180-degree back, and 1342 front; each reference gets 30 frames of light/Sky warmup, each capture gets 3 frames plus post_draw. Weather is frozen at time 0.05 for reproducible local lights. Supplemental +350m lateral motion requires clear start/end sphere checks, a complete sphere sweep and a clear ray. A blocked original sweep remains a failed/blocked mobility result and produces no invalid translated image. Ordered +150/-150/+75/-75/+30/-30m sphere/ray sweeps then select the first clear supplemental path, recorded and named separately; this proves only the selected short camera path. Original reference camera poses remain unchanged. Material/render checks and original-path mobility checks have separate result fields; complete physical flight remains false. This explicitly avoids 44's known 1128 translated terrain penetration.

Required visual review: compare highlight clipping, terminator softness, cloud underside volume, moonlight readability and unintended washed-out flattening. Material quality does not establish fixed geometry/composition, complete 21-reference fidelity, or hardware rendering acceptance.

## Parent execution runner

`/workspace/shared/m.sh` is prepared, executable and bash syntax-checked, but was not executed. It first builds 45 with the normal Compatibility rendering backend, then runs 44 baseline and 45 comparison using the same verifier and fresh isolated output/userdata. Separate stdout/stderr/exit-code logs, source snapshots, a copy of the build report and paired-pose report are retained. Baseline 44 SHA is checked before and after; existing 45 is never overwritten. Paired report requires matching image names, transforms, FOVs, references and dimensions. Visual comparison still requires independent actual-image review.
