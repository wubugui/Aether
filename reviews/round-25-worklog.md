# Round 25 — actual street-side earthworks

Full session Goal remains active: all 20 new references and the original scene in one flying world. Production remains 17e/18c/19h. The reviewed limited baseline remains 24m paving plus 24l cut-only headland; no 25 candidate has been installed.

## 25a–25c rejected studies

- 25a widened the grading collar to 4 m but introduced new shore boundary vertices (170 vs original 134). Preparation retained, no Blender/GPU build.
- 25b clipped the collar 0.35 m inside the original coast. Preparation: 6870 vertices, 13604 triangles, 134 boundary edges. Native build rejected one microscopic face of area 5.720425e-10 m²; rejected editable BLEND and logs retained. No GPU run.
- 25c uses the same 25b field and collapses only recorded sub-2-mm degenerate edges. Native build and reopened twelve-component check passed; original eleven rock meshes unchanged. All five GPU stages terminal passed in `village-paving-25c-20260908T140040Z-542f147b2e5043ea9e91bb591f0cb494`; root and independent reviewer viewed all five. No pending 25b/c process.
- **25c visually rejected.** High roadbed walls recede but radial sharp faces and long dark creases appear. Actual exposed slopes reach 88.0158°. Complete evidence: `round-25c-village-earthworks-independent-review.md/json`.
- Actual 12083 cap triangles have no penetration, but bay clearance is only 2.2623 mm. Nine main house body foundation regions retain original height within 0.03861 mm; forward doorstep ground intentionally changes by up to 0.40416 m and must not be called unchanged. All 134 coast coordinates and 2937 original bottom/side/rock triangles retain exact geometry/materials.

## Diagnosed causes and 25d in progress

`captures/diagnose_25c_field.py` maps actual steep triangles back to field constraints. Bay vertices only 7.21 cm apart have weights approximately 0 and 1 because the collar's coast-clipped edge sits beside the road footprint. The foreground 88° triangle spans a nonlinear field with nearly collinear vertices: separate analytic vertex samples do not bound its actual face gradient.

25d adds a one-metre planar grid only inside the collar (10393 vertices, 20650 triangles, original 134 boundary). It resolves actual mesh heights with explicit per-face slope bounds and full cap-intersection constraints before Blender authoring. Original outside/protected vertices are fixed. These are design constraints, not evidence of native or visual acceptance. Its initial LP is infeasible; removing slope constraints is feasible, minimum uniform gradient slack in its diagnostic is 0.044802. This first solver incorrectly queried all original top layers including overlapping rock components; 25e isolates the largest connected core, as the Blender builder does. 25e initial strict solve is also infeasible; its diagnostic is running. No 25d/e native build or GPU has begun.

25e's core-only diagnostic has the same 0.04480144 minimum additional gradient. This correction did not change the measured conflict. 25f explicitly uses max(0.80, abs(original component)+0.05); it does not remove the real-face gradient checks. The LP passed all 120288 inequalities (66612 face-gradient, 53676 cap-overlap), numerical residual 5.19e-9. This proves the design inequalities only.

25f actual editable Blender build and reopened native gate passed. Twelve components remain; original eleven rocks unchanged; original 134 shoreline vertices reused. Native build PID5248 and gate PID30616 are terminal. Five-GPU run `village-paving-25f-20260908T142029Z-3a929b3fadd3459883fbdc78e6dae14e` is terminal passed, root exec session65095 ended. Root verified all146 bound artifact hashes and directly viewed allfive images; minimum runtime sampled clearance0.0598297m. Independent actual geometry and allfive visual views completed: `round-25f-village-earthworks-independent-review.md/json`.

**Retain the local fill repair, not whole-reference acceptance.** Prior four 25c severe slope regions now max42–48°, long black radial crease gone. Actual12083cap triangles have no penetration (min47.959mm), nine main-body foundation regions preserve old heights within0.0231mm; 134 coast coordinates and2937 lower/side triangles exact. Smaller triangular green fill facets remain. Extremely thin exported triangles can exceed design gradient bounds: the largest angle89.58° is beneath paving, and tiny exposed examples are recorded independently. Do not claim every actual exported face obeys the LP inequalities. Forward doorstep ground changes remain intentional and separate from body preservation.

Authoritative new evidence: `round-25f-root-evidence.json`, `reference-view-1342-progress-25f.json`. All25 processes ended. Next visual priority is the repeated scalloped contour-stair edges; original large bare coast walls, water, moon/cloud/light composition and full20-reference scope remain unfinished.

Do not rerun 25a/b/c/d/e. Preserve all rejected evidence. Next: inspect actual export geometry and five GPU views, then independent review. The complete reference goal is unfinished.
