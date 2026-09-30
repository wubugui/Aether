# Distant bank44 asset candidate

## Diagnosis and design

Read GOAL.md and MIGRATION_HANDOFF.md, original `model_clouds41.py`, original `hub-cloud41/cloud_sea41.blend`, references 1343 and 1128, and existing `evidence/cloud43-source-rays.json` before modeling. Original bank0 is 3333 x 1788 x 300; bank1 2720 x 1638 x 393; bank2 3196 x 1693 x 363. Their eight flattened closed lobes produce almost continuous undersides when tiled at 1400 spacing. The saved original CPU front/back/underside PNGs show this explicitly.

44 replaces the asset's two-row blanket with three offset groups. Each has crown, two shoulders, rear lobe, convex belly, and two small taper lobes. All are real closed surfaces. Their shoulders overlap locally, while groups have deep silhouette notches or air gaps. Height varies continuously and is never clamped to a flat underside. Blender vertical Z is exported as Godot Y. Pivot remains (0,0,0); original world placements, rotations, and scene nodes were not edited.

## Deliverables

- `cloud_bank44.blend`: editable native source, three separately named collections
- `cloud_bank_44_0.glb`, `cloud_bank_44_1.glb`, `cloud_bank_44_2.glb`: exported variants, exact copies under `project/assets/clouds44/`
- `model_cloud_bank44.py`: deterministic Blender 4.5 generation/export/preview script
- `cloud_bank44_preview.blend`: isolated CPU preview rig, separate from modeling source
- `bank44-{0,1,2}-{front,back,underside}.png`: nine actual CPU Cycles asset renders
- `original41-{front,back,underside}.png`: three original-asset CPU renders
- `inspect_bank44.py`, `original41-inspection.json`: reproducible old-source bounds/object inspection
- `verify_bank44.py`, `bank44-footprint-rays.json`: native exact triangle ray footprint comparison
- `cloud_bank44-report.json`: dimensions, manifold checks and GLB SHA256

Run scripts with `/workspace/shared/feiting-tools/blender-4.5.14-linux-x64/blender -b -t 6 --python <script>`.

## Measured result and limits

Each variant has 21 closed mesh parts, 2400 triangles, zero nonmanifold edges. Dimensions are approximately 1604 x 673 x 469, 1478 x 668 x 500, and 1529 x 676 x 482 (Blender XYZ). Original banks had 8 parts and 640 triangles, so draw submissions/triangles increase. At 56 distant instances this is 1176 mesh parts and 134400 triangles before engine optimization.

Fixed-grid vertical footprint ray hits indicate ~89–90% lower occupied area per bank than41. This compares world-axis source geometry only; it is neither projected camera coverage nor proof of a visual match. Original/new preview cameras use different orthographic scales (3400/2050), so PNG size is not a scale comparison.

All twelve rendered images were visually inspected. The new underside is sculpted and discontinuous instead of a broad slab, but crowns still share a family resemblance and can read as stony forms in neutral isolated lighting. White material is diffuse with no emission, no unlit override, no billboard, no image background, no screen-space tint, and no camera-directed geometry. Preview background is a uniform world shader.

Status: ASSET CANDIDATE, not visual acceptance. Needs distinct integration scene and repeated original reference cameras, side/back and flight views using real Godot hardware GPU. Existing cloud41/42d/43 scenes, old source assets, and protected cliff master were not edited. Potential new problem: the substantially smaller footprint may look too sparse in1128 or high-altitude views. Do not fix that by restoring an all-covering flat base; judge regional arrangement and weather only after real runtime evidence.
