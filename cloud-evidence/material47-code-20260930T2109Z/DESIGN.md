# Candidate47 prepared composition, not executed

Candidate47 starts from the serialized Game46 scene and applies exactly the material-only Lambert Wrap policy tested in Game45. Nothing is copied from Game45 geometry; no geometry, transform, cloud density, light, camera, environment, albedo, vertex color, roughness, emission or brightness setting is changed. This cannot repair geometry by making it brighter.

Actual Game46 serialized preflight (`static-material-inventory46.json`) confirms 1333 single-surface target MeshInstance3D nodes: 25 CloudSea, 132 UpperCloudBank43, and 1176 DistantCloudBank41 surfaces, using nine StandardMaterial3D source resources. All retain vertex-color albedo and roughness=1 native default. The counts are checked again at runtime, and every material type and source property is checked before assignment; these are not guessed counts.

Prepared files:
- `tools/build_cloud_material47.gd`
- `tools/verify_cloud_material47.gd`
- `/workspace/shared/n.sh`

Both Godot 4.5.1 static parses and shell syntax passed. No GUI/build/verification run occurred. Candidate47 directory is empty. 45 and 46 scenes are unchanged; `baselines.sha256` records both. Run only after the parent has reviewed actual 46 imagery and approved proceeding with this composition experiment.

The builder retains Game45's proven deterministic NodePath normalization (explicit type plus exact path text), recursive dictionary ordering, complete stored world/node/resource fingerprint, target materials' all-properties-except-diffuse comparison, source-copy cache, surface-aware overrides, unmodified double-snapshot control, exact MultiMesh buffers and save/reload gates. Every failed gate reports actual detailed differences then exits 1 with scene cleanup; no existing Game47 may be overwritten. Off-tree Sky lifetimes retain 3 frames plus post_draw; exit retains 8 cleanup frames.

The verifier compares Game46 baseline against Game47 at the unchanged 1343/1128/1216 front/side/back poses and 1342 front. Light warmup, frozen weather and capture timing match. Original +350m camera sweeps remain explicitly blocked when obstructed. Only independently clear +150/-150/+75/-75/+30/-30m fallback sweeps can produce separately named supplemental images. Original reference positions never move. Material/render check outcome, mobility outcome and visual/hardware acceptance remain distinct; full physical flight and visual/hardware acceptance are false.

The wrapper builds once with an actual rendering backend, then captures baseline46 and candidate47 in new independent log/evidence directories. It snapshots tools, checks both 45 and 46 SHA preservation, and checks pairwise camera transforms/FOV/reference/dimensions and image names. Passing these checks is not visual acceptance. The parent's existing limited 45 visual review covers only two actual pairs (1343 and 1216-side); it does not establish 1128, 1342, 46 or 47 fidelity.
