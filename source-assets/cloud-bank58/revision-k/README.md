# 58K: one authored volumetric envelope, source-only preparation

K replaces J2's construction instead of adjusting its cage angles or optimizing
its slope statistics. J2's saved source, two original views, all failure evidence,
and the earlier rejected H/I/J designs remain untouched. K has **not** been run
in Blender or Godot, saved as a native source, rendered, or integrated in the world.
The complete GOAL and visual acceptance remain false.

## Reference and deliberate construction change

The author actually viewed `ref/1216.png`, plus the J2 front and side/back original
PNGs in `cloud-evidence/cloudbank58j2-contact-v1-20261002T064602Z-jf2pmotn/outputs`.
J2's large diamond roof, projecting thin shelves and dark cut-between-layer
shadows do not read like the reference's substantial cloud masses.

K is a single explicitly authored skin around three unequal swollen lobes. Sixteen
irregular twelve-point sections run through a smaller forward lobe, a dominant
higher middle lobe and a medium rear lobe. Their depth centers are staggered
(-42, +17, +65 m). The authored crown ordinates are 800, 852 and 825 m. Two
substantial saddle sections have 171/173 m full width and 146/141 m vertical
thickness. The lower sections form one continuous belly, with no separate
carrier, lower block, overlaid roof, Boolean seam or recessed sandwich cut.

Every section, angular station, shallow longitudinal lean and strip diagonal is
stored directly in `design58k.json`. Unequal angular intervals and section spacing
provide large and medium facets across the surface. The highest shoulder has
multiple short changes of slope rather than one giant roof plane. Tip fans cap
small end sections; no thin horizontal shelf is appended. This is one deliberate
authored candidate, not a parameter sweep or random triangulation. No geometry
parameter was changed after its first passing probe (`candidate-probe58k.json`).

This construction is still a visual hypothesis. Longitudinal faceting or joined
mounds may remain perceptible; mathematical results cannot settle that question.
The future unchanged front/side original views require independent visual review.

## Intentional semantic-control redesign

The historical eight intersecting cages are replaced by six native Empty handles:

1. Left_Forward_Lobe
2. Main_High_Lobe
3. Right_Rear_Lobe
4. Left_Broad_Saddle
5. Right_Broad_Saddle
6. Continuous_Belly

The six handles apply stored convex affine deformation weights to the single
rest envelope. The JSON retains immutable rest centers separately from effective
edited centers. Small changes to every handle are individually tested. These are
semantic deformations, not six separate visible meshes. Extreme edits can fold a
mesh and are rejected by the same topology/intersection/contact gates before the
native mesh is replaced. No generalized safe editing radius is claimed.

`CONTROL58K.json` is the persistent complete ring/angle/diagonal authoring recipe;
`POLY58K_math.py`, `CONTACT58K_check.py` and `EDIT58K_rebuild.py` are embedded into
the future source. Explicitly run the rebuild text after editing handles or the
recipe; it neither saves nor renders. Native vertex groups store the actual
weights. Per-face semantic region and authored patch attributes, plus per-vertex
station and sector attributes, preserve editable authorship and provenance.

## Source-only result and its limits

- 194 vertices / 384 triangles / 576 edges; one component, Euler 2, positive volume
- Consistent two-face directed edge incidence and one-cycle links at every vertex
- Original limits remain 800 vertices / 1,600 triangles; no topology waiver
- Original tolerances are identical to J2, including intersection/contact 1e-8 m
- Both double UVY and source-basis float32 predicted arrays pass all AABB-overlap
  triangle pairs, including shared-vertex pairs, and supplemental contact checks
- 2,693 double / 2,601 float32 AABB pairs; no coplanar pairs in this candidate.
  Coplanar zero-area contact behavior is separately exercised by negative controls
- Maximum source-basis float32 displacement: 0.0000314491 m, below 0.0001 m
- Minimum edge: 14.3289 m; minimum triangle area: 204.556 m². There are no union
  clipping fragments. Triangle areas and surface slopes are recorded only as
  diagnostics, never promoted to cloud resemblance or a scoring objective
- Fixed E camera predictions: 25.6873% front margin / 11.3210% side/back margin.
  Both must still pass the unchanged 7% gate on the actually opened native source
- All six semantic surface regions remain exposed. Old eight-cage projected-area
  gates are intentionally retired with that architecture; no claim is made that
  an absent historical cage is still an editable K region

Topology incidence is combinatorial. Intersection/contact and float32 checks are
numerical, not an exact-arithmetic theorem. A separate float32-matrix arithmetic
control passes, but actual Blender Empty decomposition and saved arrays have not
been tested. Source size remains unverified until the real native trial.

Normal and optimized Python each pass 33 math controls and 36 contact/readback
protocol controls. No `assert` is relied on. The inherited topology, fingerprint,
source-basis and intersection function bodies are byte-for-byte copied from J2;
the supplemental contact function bodies are unchanged too.

## Prepared native pipeline, not executed

`run_patch58k.py --run-approved-patch-trial` is the single later scheduled entry:
one source build, one independent fresh saved-source verification, then the two
original fixed-camera views in separate processes. It retains the audited J2
resource wrapper and actual-array contact protocol, with only local candidate
paths and freeze layout adapted.

- Entire future trial: 30 seconds, CPU2, 1.5 GiB conservative wrapper-plus-child
  peak limit, compressed source at most 200,000 bytes
- Same E front/side camera matrices, projections, resolutions, sun, world,
  material, exposure and CPU render settings; no auto-fit
- Saved-source dependency readback must contain no images, external libraries or
  strongly linked IDs. Embedded control/code hashes and complete native identity
  must match the built source
- Fresh verify checks geometry arrays from the actually opened native mesh.
  Rendering is blocked on missing/failed contact proof, wrong source/array/code
  SHA, changed verification result, or reused verification process
- Original source/protected evidence and all preparation inputs are checked before
  and after stages. Source, failure logs and images cannot be overwritten

The entry has only been AST/protocol tested. **No native process has been started
by K preparation.** The parent schedules any native window separately. Git,
publication, `CLOUD_RESUME.md`, Slack and all existing native assets were not
changed by this task.
