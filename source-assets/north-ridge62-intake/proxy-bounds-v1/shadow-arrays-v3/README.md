# Shadow arrays v3: narrow source-read compatibility correction

Source preparation only. No engine, new download, main-project/terrain/scene/asset edit, Git, progress-document or Slack action. Original v1/v2 preparations, freezes and both failed native reads remain unchanged.

## Bounded change

The v2 read passed the exact engine gate, then stopped at the first position-only compressed shadow's null API vertex array. The independent `shadow-diagnostic-01` replay established all 120 primary vertex bytes and all 168 actual snapped `get_faces()` bytes exactly, plus equality of the primary/shadow 56 oriented triangles. This supplement uses that existing compatibility path rather than inventing a loader or adding a world audit.

`visible_geometry61.gd` is an unchanged byte-for-byte copy of the existing strict nearbay helper, SHA256 `966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7`. The new collector calls only its pure `surface_positions`, `audit_surface`, `oriented_triangles` and `audit_array_mesh` methods. It never calls its world/PhysicsServer preparation or shape functions.

The helper checks actual packed position/index payloads against native APIs when available, permits the specific compressed no-normal null-vertex shadow branch, and requires primary/shadow oriented triangle multisets to match at base and every saved LOD. Winding, multiplicity, complete thresholds and surface identities remain strict. The metadata AABB supplies the compression decode scale/origin; it is not substituted for decoded geometry.

The collector inherits v2 initialization/full engine-hash checks and the original six visual-source and first-imported-rock bindings. Only `mesh_summary`, its small reporting helpers, and full-precision JSON serialization change. The terminal writer is otherwise byte-identical to v1; its full-precision option is the existing successful scatter-collector contract, preserving float32 extrema exactly through JSON rather than introducing an epsilon. Existing saved-source/material/transform/tile protections remain intact.

## Two different actual products, no epsilon

- `vertex_bounds`, legacy `face_*` with explicit `face_method=actual_indexed_base_faces`, and `indexed_visual_bounds` describe decoded/raw native visual vertices and their actual indexed base/all-LOD triangles
- `get_faces_*` describe the separately observed primary `Mesh.get_faces()` result. Its entire byte hash and extrema must exactly match the indexed base faces after the fixed float32 0.1 mm `Vector3.snapped` operation; the step-byte witness must equal `17b7d138`
- Shadow meshes are decoded and fully checked but never queried through the unsupported `get_faces`/missing-vertex API path. Their primary-equivalent drawn coverage is established by exact all-level oriented multiset checks
- `combined_clearance_bounds` is the exact union of raw vertex/shadow, actual indexed visual, and actual primary get_faces bounds. Snapped coordinates may extend beyond unsnapped extrema; no containment epsilon is introduced or enlarged
- The runtime rock oracle is the actual imported primary `get_faces_bounds`, because that is precisely the unchanged `open_world.gd` collision source

The Python protocol retains every original v2 engine/binding and v1 indexed-geometry shape check, then validates the added all-level coverage, snap witness, primary-only API usage and exact unions. Legacy indexed faces still require exact containment in the raw vertex domain; separately snapped faces require their exact byte/bounds witness.

## Same query and stopping point

`analyze_shadow62.py` reuses the original complete saved-buffer replay with exactly three checked textual substitutions: deriving the v3 request, selecting the explicit clearance union, and naming that output field accurately. Its decoder, 775-group/57,797-instance coverage, visual baseline replay, source transforms, tree rule and coast61/coast56 protection are unchanged. The new rock oracle is supplied by the stricter v3 validator.

One future scheduled read still covers only the same six visual identities and first imported rock mesh. There is no extra exploratory engine run, full-world buffer dump, new occupancy audit or terrain work. The completed path/index keep/reconcile list remains the stopping point before the constrained north-mountain work.

## Reproduce preparation / later scheduled read

From Aether, the default is pure source verification:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-arrays-v3/run_shadow62_v3.py`

Only when the parent schedules the existing engine window:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-arrays-v3/run_shadow62_v3.py --collect`

The latter uses the unchanged single-child CPU2/60-second hard-kill launcher, fixed binary SHA, full dependency/startup/remap guards, isolated absolute XDG, copied-script/request hashes and error rejection. It writes a fresh `north-ridge62-shadow-arrays-v3-*` evidence directory. Failure is preserved; no automatic retry is configured.

All 60 pure test groups pass normally and with `-O`: the 29 prior groups plus 31 focused geometry/protocol/integration groups. Separate source review found and corrected a wrapper token-guard mismatch, now covered by regression. `TESTS.log`, `TESTS-optimized.log` and `INDEPENDENT_REVIEW.md` describe source verification. `FINAL_SHA256.json` freezes all preparation files; `provenance.json` binds the existing failures, exact diagnostic and original helper. Native parsing/execution, actual completed mesh read, live collision, full occupancy and visual acceptance remain unproved until their own required evidence exists.
