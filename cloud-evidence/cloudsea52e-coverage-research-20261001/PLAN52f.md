# CloudSea52e continuity failure and smallest next experiment

Status: read-only diagnosis and proposed geometry scope only. No52f source, prefab, scene, shader or graphical run has been created. Preserve52e and its interrupted observation run as failure evidence. Full GOAL remains unaccepted.

## What was actually viewed

The reviewer opened actual pixels from `ref/1216.png`, original saved51b `1216-front.png`, and saved52e `1216-front.png` and `1216-side.png` in `../cloudsea52e-paired-20261001T050129Z-geTptG`.

52e improves local round crown, offset shoulder and curved belly forms. It removes the old huge continuous skirt occupying most of the foreground. However, the new forms read as isolated floating clusters. Broad dark channels expose terrain/island roots and the distant dark background between clusters, especially through the lower half of1216front and across1216side.

In the reference, dark cloud valleys still contain staggered inner bodies and occluding cloud walls. The sea is layered in depth. The needed connection is actual low cloud volume behind and beneath upper crowns, not a brightness change. The upper43 balls, moon/light response, missing lightning, airship framing and overall reference mismatch are separate unresolved issues; this proposal does not change those layers.

## Reproducible geometry evidence

Run `python cloud-evidence/cloudsea52e-coverage-research-20261001/analyze_coverage.py` from the repository. It reads the actual46 and52e exported GLB triangle positions/indices and the exact25 saved51b CloudSea root transforms.52e was built at these same roots. The46 source follows the preserved46→51b geometry lineage; this is a source-geometry calculation, not a re-extraction of the saved51b engine mesh.

It samples triangle unions, never fills an AABB or convex hull. The top-down region is the interior3.45km square, x1475–4925m/z1275–4725m, sampled at10m. Reference projection masks use the actually recorded51b1216 camera transforms, FOV62 and near plane, at295×166 sample resolution. Diagnostic masks exclude every other world object, all lighting/materials and HUD. They are not engine screenshots, reference similarity scores or proof of surface/flight clearance.

| Measurement | Old46 geometry retained in51b |52e |
|---|---:|---:|
| Interior sampled top-down triangle coverage |93.96%|35.24%|
| Interior uncovered fraction |6.04%|64.76%|
|1216front lower-half projected coverage |100.00%|54.47%|
|1216side lower-half projected coverage |97.67%|66.28%|
|1216back lower-half projected coverage |84.38%|59.02%|
| Median top visible cloud height at covered samples |821.4m|913.3m|
|90th-percentile top visible height |986.8m|1009.7m|
| Largest connected empty sampled area |0.093km²|7.708km²|

The source-scale gaps are systemic: the new upper shape range stays near the old maximum, while low trough coverage disappears.52e's extensive connected empty area means nudging one crown or adding a tiny join between its own three pieces will not restore the sea. The source worker's per-variant horizontal gap measurements already show132–210m gaps between main/shoulder,162–202m shoulder/tail gaps, and much wider main/tail separation. Those intra-variant gaps are only part of the cross-root coverage deficit.

Exact input hashes, camera matrices, coverage values and limitations are in `coverage-report.json`. The generated height maps and1216 masks are explicitly diagnostic. Boundary empty-circle estimates in that report are clipped by the chosen region and must not be treated as world-wide maximum hole sizes.

## Scale hierarchy is a second, independent defect

The visible foreground group is about one-third of the actual1216 image width. `probe_screen_scale.py` casts rays through the source52e triangles at the recorded51b camera pose. It identifies `CloudSea_0_1/CloudSea52e_v0_low_tail` in the front foreground, with a projected part bounding width33.44%, and `CloudSea_0_0/CloudSea52e_v2_main_ridge` in the side foreground, with a projected width33.46%. The geometric bounding box is not an engine object-ID silhouette; other pieces and world objects may overlap it. Because52e's runtimeJSON was lost, these are intended-pose geometric diagnostics, not recovered runtime metadata.

Large foreground mass alone is not a defect: the reference also has large foreground cloud groups. The distinguishing problem is that52e resolves those groups as a few near-equal huge rounded crowns. The reference's large groups contain intermediate shoulders, small stepped edge lobes and internal troughs. Current source controls confirm the narrow size range: large lobe radii are145–190m before final normalization, while most secondary radii are80–140m. There is little genuinely small shoulder structure. Adding two smooth oversized bridges would repair area coverage while preserving this weak size hierarchy.

The next source must combine coverage and hierarchy. Begin with large crown diameters roughly250–400m, medium shoulders90–200m and small edge/valley lobes35–90m as provisional source design ranges. These are proposed dimensions, not measured reference scale. Small lobes should be grouped into meaningful shoulders and bends, not sprinkled uniformly or represented by surface noise. Their volume must survive union/decimation and change the actual silhouette from side/below as well as above.

## Minimal next candidate52f

Start from immutable saved52e. For the first controlled continuity experiment, retain the75 existing upper meshes and add low connector/shoulder volume beneath and around them. An initial sizing budget is about two closed low bodies per root, roughly50 new nodes, with three different source arrangements. This is an experimental starting budget, not a user constraint or an acceptance condition. Actual per-root counts may vary where real neighbor gaps require1–3 bodies, and a dominant upper or tail mesh may be resculpted if the resulting source still reads as a few giant balls. Keep every such change in the exact mesh/property ledger. The user does not require three existing pieces or a fixed number per tile.

The unchanged boundaries are the25 original roots, their world transforms, original active material behavior and all unrelated world state. No world generator, other cloud layer, controller, terrain, weather or material change is proposed.

Each root receives two differently shaped, offset lower bodies:

1. A bent low saddle crossing the main/shoulder gap and extending toward a root boundary. Start the design envelope at roughly900–1200m long,400–550m average width, with an irregular fork or neck. Its staggered top lobes should occupy localY≈−20…+140m (world680…840m), and its rounded belly should vary down to localY≈−130m (world570m). These are design ranges, not measured source geometry
2. A lower trailing drift crossing the shoulder/tail gap and turning toward the complementary root boundary. Start around850–1150m long and400–550m width, at a different height and yaw from the first body. Give it unequal lobes, a narrower curved waist and ends that fall away inZ/Y; do not make two uniform parallel strips

The initial two bodies should be made by unioning unequal editable medium/small lobe volumes into separately closed shells, with noncoplanar curved undersides. Their upper shoulders should climb partway along the existing large crowns to establish the missing intermediate scale, instead of merely covering dark pixels far below. Source controls must survive. A single common flat bottom, a global cloud sheet, one repeated circular puck and thin camera-facing pieces are prohibited. The bodies may overlap existing volume intentionally where the saddle disappears beneath a crown, but visible crossing seams or disconnected tangencies require actual multi-angle review.

The envelope sizes address a net deficit of about0.49km² per1.3225km² root-spacing cell if the next experiment aims to reach roughly72% sampled coverage. That target is only a diagnostic improvement threshold, not a reference acceptance criterion. Exact controls should be chosen by recomputing real source triangles at all25 actual root rotations before engine integration. The initial two-body budget is a bounded proposal with enough potential area to test the dominant coverage failure; its sufficiency and optimal count are unproven. Do not let that budget prevent required scale/hierarchy improvements.

Vary the bend, branching and height arrangement across the three variants. A new variant should not be a uniform rotation/scaling of the other two. Local endpoints must be adjusted after inspecting neighboring world placements; simply adding equal-width ribbons to every root would repeat the same grid problem.

## Evidence required before and after integration

- Reopen the new Blender file; verify two independent connected/manifold shells per variant, positive volume, no zero-area triangles or non-adjacent self-intersections, retained editable controls and actualGLB axis mapping
- Recompute triangle footprint coverage using the same interior grid. A useful first experiment should increase coverage into roughly70–85%, with several deliberately bounded low valleys instead of one enormous connected empty channel. This threshold is provisional; it does not authorize hiding all gaps
- Recompute1216front/side/back triangle masks. Aim for at least85% lower-half coverage in front/side while keeping upper crowns' world maxima and positions unchanged. Do not obtain this by raising a single broad slab into the view
- Inspect real source front, side, back, above and below views for all three variants. Reject shared planar bottoms, uniform bowl profiles, long smooth strips and highly repeated lobes before saving a world candidate
- Save52f as an independent candidate from52e. Prefer an additive first experiment to isolate the dominant density defect, but allow documented CloudSea mesh resculpting and variable connector counts if needed for multiscale form. Audit exact added/removed/changed CloudSea paths; preserve every root and every unrelated saved property, ownership, connections, material/guard paths and48,000 weather floats
- Use bounded single-candidate processes and atomic per-frame reports. Reuse already recorded baseline pixels; do not rerender16 baseline images merely to fill an evidence gap. If missing52e reference runtimeJSON prevents a strict metadata pair, say so
- Actual world views: same1128/1343/1216 front/+50°side/180°back; matched close views from the sides and undersides; staged climb along the same x4050/z3000 stations. Add a local oblique view through each connector neck to expose overlap seams, and a below-cloud view to reject a new ceiling
- Record actual triangle center/segment intersections, terrain camera-sphere checks and blocked routes separately. The original350m route failure and old1344 pixel gate remain false. Camera staging is not a full player-flight pass

Accept the candidate only as a further experiment if coverage improves without replacing the old skirt with another continuous flat ceiling. Full visual/reference acceptance remains a separate review.
