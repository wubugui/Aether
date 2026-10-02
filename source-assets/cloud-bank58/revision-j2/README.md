# 58J2: one certified local translation repair, math-only pass

58J remains rejected and immutable. J2 changes only the centers of
`Back_Diagonal_Ledge` and `Left_Short_Accent`; all eight local plane tables,
physical normals, scales, yaw angles, roles and metric authorship are unchanged.
No Blender, Godot, native source, image, four-root or world integration has run.
This result is mathematical feasibility, not native or visual acceptance.

## Derivation before the single candidate

The positive common-ball radius was fixed at **0.5 m before solving**. With all
other cages fixed, each repair solves the convex program

`minimize 0.5 ||delta||^2`

subject to every fixed-cage plane `N*x + 0.5 <= d` and every moved-cage plane
`N*(x-delta) + 0.5 <= d`. Normals are physical unit UVY normals, so 0.5 is a
radius in metres. This is the minimum translation for the selected cage and
fixed triple, not a claim of minimal modification over every possible redesign.

`author_repair58j2.py` uses analytic derivatives to identify active linear
constraints, then solves their KKT linear system directly. Nonnegative dual
multipliers, primal feasibility, stationarity, complementarity and a near-zero
primal/dual gap certify the global minimum. A separate linear program minimizes
distance along the solved direction and independently obtains the same length.
The code does not enumerate shape parameters or trial geometry candidates.

- Back mound, closing Main / Rear / Back: UVY translation
  **(-1.0033604133, -11.6578495101, +10.6782409531) m**, length **15.8409916726 m**
- Left accent, closing Main / Front / Left: UVY translation
  **(+7.7507244281, -0.1465180444, +2.0880407530) m**, length **8.0283940413 m**

Both solve within the predeclared 40 m local-motion cap. The original failed J
intersection radii -4.2467041404 / -2.0295176838 m become
+0.500000000000057 / +0.499999999999964 m (floating arithmetic).
The largest independent KKT stationarity residual is 2.49e-14; absolute duality
gaps are below 2.6e-13. Full matrices, source identities, active planes, duals,
witnesses and solver metadata are in `translation-derivation58j2.json`.

`design58j2.json` is the only derived candidate. It is persistent reusable
local-plane authoring data. Rebuild reads its stored local planes and edited
Empty transforms; it never reruns the metric-authoring or translation solver.
No candidate parameter was changed after testing.

## Actual math result

`candidate-probe58j2.json` passed the existing union, manifold, genus, intersection,
float32, semantic exposure, fixed-camera and projected-area gates:

- **665 vertices / 1,326 triangles / 1,989 edges / Euler 2**, one closed,
  consistently oriented genus-zero surface with one-cycle vertex links
- Original limits remain **800 vertices / 1,600 triangles**; no genus waiver
- Original polygon/edge/classification/weld tolerances and 1e-8 m intersection
  checker are unchanged; `poly58j2.py` is byte-identical to `poly58j.py`
- Both double and source-basis float32 coordinate topology/intersection checks pass
- Maximum float32 displacement **0.0000305053 m**, below original 0.0001 m bound
- Minimum triangle area **0.000544604 m²** (float32 **0.000544044 m²**), minimum
  edge **0.0236275 m** (float32 **0.0236135 m**). Small clipping fragments remain;
  they are not claimed as authored medium-scale shape details
- Actual exposed-union triangle area is **96.7384% at 15–60°**, **0% within 15° of
  horizontal**, and **0% within 15° of vertical**. This preserves J's physical
  slope intent, not proof of a convincing cloud silhouette
- All eight regions retain exposed area. Fixed side/back centroid-visible areas
  are 13,828.39 px² for Back mound, 16,016.22 px² for Front lower return and
  10,138.15 px² for Rear lower return, above the unchanged 1,000 px² gates
- Original E camera transforms/projections and lighting/material inputs remain
  fixed. Static full-source margins are **24.3449% front / 12.1678% side/back**,
  unchanged at the measured extrema. J2 explicitly requires **7% in both views**,
  rather than relying only on the inherited side/back margin gate

## Complete overlap-change audit

`repair-audit58j2.json` independently rebuilds the certificate constraints from
frozen J, checks exactly the two changed center fields and all unchanged metric
normals, and evaluates every pair/triple for both fixed designs. Higher sets
are skipped only when an already-measured subset has no positive overlap.

- The same **12 positive pairwise overlaps** remain; none is added or lost
- Positive triples increase **3 → 5**, exactly the two intended triple fillings
- No previous positive overlap is lost; no other positive overlap is created
- No all-pair-overlapping triple remains empty; no four-or-higher common
  positive-volume intersection occurs
- The nerve audit supplements the actual surface genus/intersection check;
  it does not replace that gate
- **692 historical source/evidence inputs**, including all J failures, are SHA
  checked unchanged. No earlier source, diagnostic, log or report was repaired

## Tests, freeze and native pipeline preparation

Normal and optimized Python each pass **12/12 mesh controls** and **16/16
certificate controls**. Certificate negatives include changed normals/supports,
changed stored translation, infeasible witness, negative/zero/perturbed duals.
The preserved mesh controls cover holes, duplicate/reversed faces, disconnected
regions, degenerate scale, coincident cages, slivers and illegal intersections.

`check_preparation58j2.py --freeze` repeats the identical candidate
fingerprint and semantic owners, rechecks mathematical gates and protection,
AST-parses every prepared script, and freezes the source-only package.
Read its actual result in `preparation-check58j2.json` and identities in
`preparation-freeze58j2.json`; the redirected final log is sealed separately by
`preparation-terminal-freeze58j2.json` so an open output stream is never treated
as immutable input.

Prepared native entry points preserve eight editable Empty controls, eight
semantic groups, per-face region/plane attributes, and embedded JSON/math/rebuild
texts. One later, separately scheduled trial may run `run_patch58j2.py` using
the explicit `--run-approved-patch-trial` flag: one build, one independent fresh
saved-source verify, then two fresh original views, within the unchanged
30 seconds / CPU2 / 1.5 GiB / 200,000-byte source limits. Every stage keeps full
logs, dependencies and actual exits; no source cleanup or rerun in place.

**Not tested:** actual Blender transform decomposition, native saved-source size
and editability, fresh dependency readback, render success, visual quality,
world integration or complete GOAL acceptance. The parent must review this
source-only result before scheduling a native window. Git, publication and
CLOUD_RESUME were not changed by this preparation task.
