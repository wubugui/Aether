# North-ridge62 scatter hit classification

Completed offline, source-bound review. No engine, project/terrain/asset/orbit edits, Git, CLOUD_RESUME or Slack actions.

Raw native report: `cloud-evidence/north-ridge62-scatter-float32-collect-20261002T065622Z-6k1gbidm/native-scatter.json`
SHA256: `62482b889a2dc6c5687274748397f5d4bf9da3be6898b8fbca6d372a5a2452bf`. Its lossless gzip was byte-compared to the raw report. All source pins and exact group/index membership are in `classification.json`.

## What constrains the footprint

33 groups contain 676 saved whole-bound-mesh AABB query hits: 575 intersect the design rectangle and 101 only its 40 m buffer. All 33 are saved visible World/Vegetation groups with all allocated instances visible. These are bounds hits, not confirmed terrain contacts, deletion permission or a final edit footprint.

| Actual binding class | Groups | Query | Design | Buffer only |
|---|---:|---:|---:|---:|
| poplar | 4 | 33 | 22 | 11 |
| oak | 4 | 79 | 48 | 31 |
| rock | 8 | 142 | 123 | 19 |
| bush | 7 | 62 | 52 | 10 |
| pine | 10 | 360 | 330 | 30 |

Class is established by actual bound mesh plus resolved prefab and effective metadata/asset_kind, never node names. The ten pine hit groups retain misleading oak/poplar names. The two -4_-6 pine groups alone account for 260 design hits. A root-only test would miss eight query and eight design hits.

Every design hit requires an explicit keep/support/reposition decision where the eventual changed terrain intersects it. Buffer-only hits constrain the blend boundary. Bushes are still visual and support constraints; lack of a runtime collider is not permission to bury them. Two buffer-only coast61 hits (one bush, one pine) belong to the protected -5_-5 neighbor resources. Never edit whole groups from these counts. Per-group union boxes are summaries only; use the pinned raw path + instance index for actual bounds and full transform.

## What the sources actually do

- All hit groups use ShaderMaterial_4hw14 in Game53dWest, no overlay or next pass. Saved cloud_drift is false. The shader's only vertex-position write is conditional local X += sin(world_time*.018)*9; it is inactive for that saved branch. This does not observe live uniform values.
- scatter_group.gd has editor tool buttons/copy/extraction functions and no automatic _ready/_process/_physics_process. model_scene alone is not evidence of runtime visual replacement.
- The concrete runtime path is world39.gd → open_world.gd. _ready (35–76) reads metadata/asset_kind and the full composed saved instance transform into layout.props/prop_transforms. refresh_collisions (289–331) skips bushes; oak/pine/poplar use radius 2.4, height 11 capsules centered at local Y=5.5; rocks use faces of model_meshes[kind], loaded from the first mesh of the imported prefab. It applies the saved full transform.
- These are conditional nearby proxies: source rules select the 3×3 focus-cell neighborhood, <=350 m horizontal root distance and <=150 m vertical difference, refreshing after >0.4 s. 472 query / 400 design tree hits and 142 / 123 rock hits are potential source-rule candidates, not observed active colliders. 62 / 52 bushes remain visual-only under this rule.

## Smallest useful next read

1. Reuse the exact saved buffers to derive tree capsule envelopes, and inspect only the rock prefab's first imported mesh/actual face extent. Pin that path before equating it with the saved rock visual resource. Runtime does not use assets/collision/rock.res for these scatter rocks.
2. Re-query visual-plus-proxy bounds, including adjacent groups outside the visual-only hit list. Capsule-only intersections could otherwise be missed. Read the few bound mesh/shadow vertex extrema needed for exact support; there are six bound resource identities and five distinct recorded primary surface-storage hashes here. No second full-world buffer dump or world run is needed for this preparation.
3. Stop once the path/index-keyed conservative keep/reconcile list and rock source identity are established, then sketch the constrained mountain footprint with existing tile/border protections. A later focused live check is required for runtime clearance, rather than treating source formulas as executed evidence.

The shader branch is a resolved saved-state fact, so hypothetical universal deformation/replacement audits are not the leading next task. The prior 172-entry saved settlement catalog has zero query hits, and all three saved road control hulls miss it; retain the old twelve-house identity and road-width booleans as unproved rather than inventing blockers or houses. The non-scatter cloud bank/weather/ocean hits remain separate height/state/composition constraints, not a blanket ground-building mask.

## Verification and limits

1974 explicit offline checks passed, including raw/gzip identity, original terminal wrapper binding, all five class totals, membership predicates, saved metadata/prefab/script/material bindings and before/after consulted-source hashes. Reproduce from Aether with `PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-hit-review-01/classify_hits.py`.

The review preserves every original unresolved flag as false: full occupancy, runtime generated/model_scene/collision geometry, full shader envelopes, road width, independently recomputed vertex bounds and visual acceptance. No original report or failed evidence is rewritten. Saved visibility does not imply terrain contact or present live visibility. No mountain asset/footprint has been approved or built.
