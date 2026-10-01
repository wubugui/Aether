# D small fold junction: first complete static check

2026-10-01 15:50 UTC. The saved context-reconstructed prototype passes this
limited static check. No model correction was made in this work item. This is
the first complete D check after the workspace reset, not recovered evidence
of a pre-reset validation. The original five reconstructed files stay byte for
byte unchanged. Their historical `geometry_passed: false` flags are preserved;
the new result is in the separately dated proof below.

## Actual result

- Saved mesh: 325 vertices, 969 edges, 646 triangles; one closed, orientable,
  consistently wound genus-zero shell, Euler characteristic 2
- Signed volume: 113,624,980.21641201 cubic metres; no boundary, loose or
  nonmanifold topology, duplicate triangles or degenerate triangles
- All 4,439 actual triangle AABB candidate pairs narrow-phase checked, including
  4,077 pairs sharing indexed vertices or edges; none excluded by adjacency
- No improper intersections or coplanar area overlaps. Only contacts confined
  to the common indexed vertex or edge are accepted. Plane tolerance is
  0.000001 m; common-simplex contact tolerance is 0.00001 m
- Three main and eight medium authored crease paths retain their knots and
  complete constrained mesh-edge chains. Eight active parent junctions are
  shared in the mesh; twelve small-fold junctions remain guide-only
- Original valley Vd: 36/36 rays pass, first surface Y 515.000–645.000001 m,
  minimum first solid interval 222.340407 m, declared floor band 480–680 m
- Original valley Vback: 18/18 rays pass, first surface Y 560.000–645.000001 m,
  minimum first solid interval 237.616586 m, declared floor band 500–700 m
- The original 25 m arc-length stations plus endpoints, three transverse lanes
  at −20/0/+20 m and 160 m minimum first interval were unchanged. Every sampled
  ray has one solid interval and no entry/exit error
- A separate float32 sensitivity check also passes. Maximum vertex displacement
  from rounding anchor-relative coordinates is 0.00002999222 m
- The local control coordinates map exactly, array-for-array, to all 325 saved
  world vertices under the declared D frame; maximum error is 0 m
- World bounds: X 3556.346665–4315.108536, Y 170–910,
  Z 3323.115480–4040.206713 m. Lowest stored vertex is 170 m above Ocean Y=0
- All 293 files named by the complete C freeze still match their recorded SHA256

## Evidence and replay

- Checker: `prototype-01/check_static58d.py`
- Run: `prototype-01/static-check-01-20261001T1550Z/`
- Full actual triangles, intersection contacts, topology, control chains and
  signed valley ray intervals: `static-proof58d.json` inside that run
- Inputs and reused frozen helper SHA256: `input-sha256.json`
- Process report and actual `wrapper.exit-code`: terminal 0, 1.261915 seconds,
  peak process RSS 41,140 KiB
- Log: `prototype-01/static-check-01-20261001T1550Z.log`
- Minimal publication list and byte hashes: `static-freeze58d-20261001T1550Z.json`

The checker loads only the pure topology function from the frozen C helper and
the existing pure triangle/ray helpers; it does not import or start Blender.
Five frozen geometric counterexamples and five indexed-contact cases exercise
legal shared edge/vertex contact, actual adjacent fold-through, positive-area
coplanar overlap and unwelded contact. All ten pass their expected outcomes.
Replay requires only installed Python/NumPy and a new output directory:

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B \
  source-assets/cloud-bank58/revision-d/prototype-01/check_static58d.py \
  --output source-assets/cloud-bank58/revision-d/prototype-01/NEW_UNIQUE_RUN
```

## Limits and next decision

This validates the saved JSON mesh, not a stored Blender mesh. Float32 rounding
is a prospective sensitivity check, not a native readback. Sampled valley rays
do not prove every continuous point of the full width or a ship flight path.
The source covers one nominal 640×625 m local junction; its angled world-axis
bounds and folded side protrusions are reported above, not hidden in that label.

No Blender binary, GLB, render, world integration or four-root expansion was
produced. The twelve small folds are still guides. No visual acceptance follows
from a closed shell, volume, ray counts or low triangle count. Rounded plinth,
empty plateau, broad belly plate or mountain-like silhouette risks remain for
actual isolated source images. A future separately authorized item may create
the editable native source and inspect it from the true 1216 camera plus full
side, back, top and underside views.

Work stopped at this first complete pass so this small item can be documented
and published immediately. Git operations and CLOUD_RESUME are owned by the
parent task; this report does not claim remote delivery.
