# North ridge62 finite continuous support pre-solve

## Result and scope

Source-only, no native process and no placement, terrain, asset, project, cloud, Git or Slack mutation. The original frozen design is `12d9f492d3ae1251d37f6b8b94e9e5877eb85dd96f723f97542a5c4885818702`.

Every one of the167 potential affected rows has an explicit result:

-31 conditional source Y candidates:28 pine,1 rock,1 oak,1 bush
-7 exact original placements retained:4 pine,2 rock,1 oak. Their visual/rock-foot geometry and tree capsule worst-contact metric did not change despite the broad bound intersecting changed terrain. This preserves historical gaps rather than silently fixing them
-117 blocked: empty pure-Y interval under the specified contact, burial, extra-seat, source capsule and unaffected-piece conditions
-12 blocked: even the highest permitted float32 Y loses too much original above-terrain surface area or top clearance

All509 query keep rows retain their original row digest, two are protected coast61 query entries. All324 protected coast56/coast61 saved instances and at least57,630 of the57,797 saved instances remain conservation requirements. This solver writes no instance buffer at all. Zero deletions. The31 source candidates are not native support passes or permission to integrate. The original167 support_proved flags remain false in the unchanged plan.

Selected positive Y translations span0.9072265625–466.91849517822266m. Large translations reflect the frozen proposed ridge relief; they are not a claim that the resulting vegetation/rock composition is visually acceptable.

## What was actually read

The existing strict `decoder62._Reader` validates each selected canonical RSRC resource, including all record boundaries/variants. Only five canonical meshes are decoded, no second775-group collection. Compressed position decoding repeats the existing float32 AABB/u16 formula. Each full decoded vertex byte sequence and ordered indexed face sequence matches the existing successful v4 native API hashes exactly.

The pine source is the protected coast61 resource with the same native primary geometry hash as the original53d pine mesh. It is read-only, not a vegetation source change. Rock, bush, oak and poplar are the actual bound canonical meshes. For rocks the raw visual/index faces additionally match the first imported rock primary mesh's actual faces. Float320.0001 snapping reproduces the entire actual imported rock get_faces byte SHA `20738d402431be5922fc6659aa80de1a7907abd3438c62ac989cca7b2e278267`. No prefab mesh-node transform is applied, matching the existing runtime rule. Raw/indexed faces and snapped get_faces remain separate.

Four-mesh mapping identity `72b6d2d6ad1c7623d3a4e81a30c2daf20641d145f97a12605936998c1a36a371` is checked. Its24,576 original GPU-index-expanded world corners exactly match the saved survey in float32; the support solver does not invent index/UV/color correspondence or reconstruct local coordinates by subtracting the world origin. The frozen candidate is applied with the original survey-coordinate keys. Consumed survey/native/wrapper identities are required to match the frozen plan before use. The14 original query resource files plus the runtime rule are checked against the pre-existing immutable-source manifest, without decoding or collecting their instance buffers. Complete input identities are in support-results.json.

Original visual/collision surfaces are not equated. Across each of the six supplied source tiles, corresponding world corners can differ by up to0.00048828125m. Both original continuous visual and collision foot results are recorded. The proposed ridge collision transfer is not yet authored/read back: the new surface is a common-surface design target, not actual physics-shape evidence. This gap blocks integration, not the isolated Blender source build.

## Continuous contact method and limits

The actual57B `plane`, `clip2`, `clip_root` and61-equivalent visible-triangle clipping helpers are imported and reused unchanged. The solver retains every component of each saved composed affine. All167 observed matrices are upright with yaw/scale; they are never orthogonalized or replaced by a scalar approximation. The analytical capsule implementation rejects any tilt/shear involving Y, singular XZ basis or uncovered capsule domain rather than extrapolating beyond its supported case.

-Tree visual feet are the actual flat six-vertex pine or seven-vertex oak/poplar root ring. Canopy bounds are not a foot
-Rock/bush feet are every actual lower rendered triangle clipped at localY=0; rock physics uses separately clipped actual snapped get_faces
-Each polygon intersects every candidate terrain triangle beneath it. TerrainY−oldFootY extrema occur at every resulting clipped vertex. Full projected-area coverage is checked per polygon
-For bounds burialB and allowed gapG, visual/rock interval is `[max(d)−B, min(d)+G]`, intersected with inherited maximum extra-seat conditions. The original G=.001m is retained, as is the .002m seating pad preference. No5cm allowance or inflated epsilon
-Any positive-area unchanged terrain piece under an otherwise affected foot requires dy=0 to retain its original gap/penetration rather than hide a historical defect. Unchanged actual-foot/rock-proxy cases and unchanged tree capsule maximum-contact metrics retain their original condition instead of being subjected retrospectively to a new contact gate
-Closest allowed root-support translation is converted to a representable float32 worldY and rechecked against the unchanged interval. No instance buffer is synthesized. The tightest selected gap-bound margin is only1.1595329851843417e-7m (pine under oak_-4_-6_CoastalPines36b index111), so source arithmetic is deliberately not promoted to native rounding/contact acceptance
-Whole actual rendered triangle surface area above terrain and top clearance are measured, not just canopy vertices, volume or five rays. If the preferred candidate fails, the highest legal float32Y is also checked; because these quantities are monotone in vertical translation, its failure blocks the interval

### Original and new geometry-relative policies

Original pine uses half its first positive **whole-mesh** layer1.7499290704727173m, with95% original visible area/top clearance. Its actual base-connected trunk upper ring is11.599926948547363m; that discovery does not loosen the existing pine gate. Original rocks/bushes retain extra seat≤one third of above-origin height, total burial≤half full model height, area≥75%, top clearance≥two-thirds.

There is no previously accepted oak/poplar-specific57B/61 policy. Their explicitly new conservative tree-family candidate uses half the smaller of their actual first positive whole-mesh layer and first base-connected trunk ring, plus95% area/top retention. Oak layers are2.8810131549835205 /4.999886989593506m; poplar1.999969482421875 /6.9998931884765625m. This is linked to each actual model, more conservative than using the trunk upper ring alone, and is not historical or visual acceptance. It does not require a separate user policy decision before the isolated ridge source is built.

### Natural capsule geometry

Source tree recipe is radiusfloat32(2.4), height11, centerY5.5. Under the retained upright affine, the bottom sphere becomes an ellipsoidal cap. In localXZ u its terrain-minus-bottom value is

q·u+c−sy·r+sy·sqrt(r²−u·u).

The continuous maximum over each triangle∩disk is evaluated analytically at the unconstrained stationary point, clipped edge extrema/endpoints, contained triangle vertices and relevant circle boundary critical point. No sampled-ray substitute is used. The enclosing rectangle's continuous terrain coverage is checked. Natural gaps toward the spherical cap edge are retained: the whole capsule projection is never required to sit flush with the ground.

The source-capsule diagnostic intersects lower support/no-air-at-nearest-point and the same geometry-relative burial bound. Godot physics-server scaling/margin/active proxy behavior has not been run; these are declared source-shape checks only. For retained tree rows, unchanged capsule max-contact does not mean every natural cap gap is identical. Geometry predicates evaluate the original saved float32 affine in float64; actual per-vertex engine rounding and contact require later native readback. The unchanged runtime focus-cell/distance/refresh activation rules are not treated as executed physics.

## Bounded alternatives, not executed terrain fixes

Each of129 blocked rows records an exact per-index bench domain (original conservative bounds plus at most8m), a proposed witness dy, low/high worldXZ triangle witnesses and the required terrainY bounds there, the ±2m necessary test, polygon containment and the full original query-neighbor list intersecting that domain.35 fail even the two visual witness≤2m test;94 pass those necessary witness bounds but are not feasible benches. Three full boxes extend outside the ridge polygon and must be narrowed or rejected: rock_-4_-7 indices28/33 and poplar_-3_-6 index0. All proposed bench boxes lie within the original query buffer, so the676-row neighbor inventory covers their spatial scope.

These records are concrete locations/constraints, not a fabricated connected support surface. Capsule/visibility constraints, protected low floor and80m wet guard, unchanged source geometry, shared seams, cloud40m clearance and every adjacent instance must be rechecked on an explicit later bench before it can be accepted. No whole forest flattening, topology change or low-shoulder relocation has been executed or claimed feasible. No relocation search is invented merely to label blocked rows successful.

The minimum next step is to pick a specific failed row/cluster in the source-form review, author a genuinely bounded bench or explicit low-shoulder relocation, and re-run that row plus the listed neighbors against the actual proposed collision surface. Rows whose required local correction exceeds2m need a different explicit proposal, never an automatic ridge redesign. World integration remains withheld until all167 have accepted exact outcomes.

## Tests, preserved failures and reproduction

20 positive/negative tests pass normally and under Python-O. They cover native full-byte geometry identities, continuous plane/foot extrema, a spike missed by a root/four-corner-ray shortcut, holes, capsule natural curvature, exact inclined-plane tangency, retained nonorthogonal horizontal affine, tilt/singular rejection, disjoint disk/triangle,30 independent smooth3D-ball constrained optimizer fixtures, interval boundaries/empty rejection, actual visual/collision differences,167/509 membership and all selected interval/visibility gates. No assert-based production gates disappear under-O.

Two preparation failures are preserved: an initial syntax error and the first result before correcting unchanged-foot preservation. An independent test's original2D SLSQP sqrt objective stalled at disk-edge singularities; its failed output is retained. The replacement test uses a smooth independent3D ball formulation; the solver formula was not loosened to make that test pass.

From Aether:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/support-v1/test_support62.py
    PYTHONDONTWRITEBYTECODE=1 python -O source-assets/north-ridge62-authoring/support-v1/test_support62.py
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/support-v1/solve_support62.py

Default solver is read-only. --write only replaces support-results.json in this directory. Reports are losslessly gzip-packaged for Git; follow STORAGE.md when the raw report is missing. The raw result, input pins and final freeze remain authoritative. No native collision, hardware GPU, renderer visibility, flight or all-GOAL acceptance is included.
