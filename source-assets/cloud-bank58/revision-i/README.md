# 58I authored polyhedral cloud: source-only preparation

No Blender, Godot, native asset or render has been executed for I. Every shape
change below is a design hypothesis. The original 1216 reference and both H
original PNGs were actually viewed. H's rounded caps, empty side-belly and hanging
bulbs remain rejected; no prior source, failed report or image is changed here.

## Representation and visible target

Eight individually authored convex halfspace cages define two unequal broad
crowns, two medium short folds, two independent lower buttresses and two small
corner accents. Each cage has a nonradial inclined roof, unequal clipped corners,
broad short cheeks and an inclined lower return. They are not ellipsoids, a
regular polygon dome, a height grid or a shared waist/bottom ring. The side/back
medium fold rises diagonally across the former empty belly; its seams terminate
locally in the neighboring masses. The two lower volumes have different roots,
depth and foot heights. Coordinates and proportions are authored assumptions,
not dimensions recovered from reference pixels.

The actual shell is the exposed boundary of the exact hard cage union. Each
face polygon is clipped against the other solids, internal faces are excluded,
all shared edge stations are inserted, coincident arithmetic intersections are
welded, then each remaining planar fragment is triangulated. No smoothing,
implicit blending, decimation, random jitter, remeshing or overlap-only visual
substitute is used. Interior coplanar partitions remain triangulated, but their
normals are the same authored plane; those triangulation edges are not claimed
as visual folds. Eight overlapping source objects are never saved as the asset.

At the original small front scale, the proof target is two unequal roof/cheek
masses separated by broad, short angular shoulders. At the fixed side/back
view, the proof target is a substantial diagonal ledge and a short recessed
valley above two unequal stepped lower returns. A new result must still be
rejected if it reads as stone caps, a boxy slab, a circumferential dark belt or
small triangles on a blank belly. Static area/projection checks are not pictures
and cannot accept the shape.

## Numerical contract and feasibility

The control JSON fixes all tolerances: plane classification 1e-8 m, weld radius
and cluster diameter 2e-7 m, minimum edge 1e-5 m, minimum positive area 1e-6 m²,
maximum float32 vertex movement 1e-4 m, 800 vertices/1600 triangles. No tolerance
is increased to force this candidate through. Nonunique parallel plane triples
are counted; ambiguous coplanar source/cutter faces fail. Zero-dimensional clip
outputs are counted. Positive-area slivers below the floor fail rather than
being deleted. No nonzero fragment is silently repaired or removed.

The final mathematical candidate has 502 vertices/1000 triangles and 79 exposed
authored planes in 202 retained clipped polygon fragments. It is one connected
closed oriented genus-zero shell. Minimum retained edge is about 0.0454 m and
minimum triangle area is about 0.00318 m²: these small clipping fragments remain
explicitly present, not silently simplified. They are numerical tessellation,
not the promised medium visible form. `preparation-check58i.json` records the
full plane-area and triangle-area distribution, all region areas, exact shared
edge-station count, weld displacement and float conversion movement.

Both float64 geometry and native float32-coordinate geometry are checked for
edge incidence/winding, one-cycle vertex links, one component, Euler characteristic, positive volume,
duplicate/degenerate triangles and triangle-pair intersections. The intersection
check includes pairs sharing a vertex, uses coplanar 2-D intersection area and
noncoplanar plane-line intervals, and permits only the common indexed boundary.
It is a bounded numerical checker, not an exact-arithmetic general CSG theorem.
Normal and optimized-Python negative tests cover 11 deliberate failures plus a
valid coplanar shared edge. None of these are Blender readback validation.

All original E camera matrices/projections, neutral light/material and render
settings remain unchanged. Fixed-camera static full-source margins are about
17.96% front and 7.81% side/back; the original 7% side/back gate is unchanged.
One centroid visibility ray per front-facing triangle records projected areas
for roof/cheek, ledge and both lower returns. It does not integrate partial
occlusion and cannot establish the rendered appearance. The first 6.29% margin
failure and the exact right-accent-only 10 m correction are preserved in
`preparation-history58i.json`; no auto-fit or crop was applied.

## Native editability and staged source validity

The future `.blend` contains one actual shared mesh, eight semantic vertex
groups (shared seam vertices may belong to both), integer per-face region and
authored-plane attributes, eight transformable Empty controls, and embedded
CONTROL58I.json, POLY58I_math.py and EDIT58I_rebuild.py. Editing a cage transform
or its plane table then explicitly running the embedded rebuild validates the
new mathematical shell before replacing the previous mesh. It never saves or
renders automatically. No intermediate high-poly, density grid or eight
interpenetrating cage meshes are stored. Native transform decomposition,
readback behavior and compressed file size remain unverified until execution.

The scheduled flow is build → independent fresh saved-source verification →
fresh front render → fresh side/back render. Startup and pre-save dependency
inventories are recorded literally. Camera append may leave transient Library
metadata; it is never cleaned or silently exempted. The initial build can only
claim `candidate_created`, never `saved_source_validated`. A distinct fresh
process must open the unchanged saved bytes and prove zero images, zero
libraries and no strongly linked IDs, together with full mesh/groups/attributes,
eight controls, embedded texts, source frame, both cameras/projections and light/
material identity. It repeats topology/intersection checks on actual loaded
vertices. Only that new-process result can authorize either render. Both image
processes repeat complete source identity/dependency checks without rebuilding
or resaving. Any failed stage stops, retaining its exact evidence.

## Commands and limits

Preparation only, no native application:

    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B source-assets/cloud-bank58/revision-i/check_preparation58i.py --freeze

Only after parent review/publication and an explicitly scheduled native window:

    OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python3 -B source-assets/cloud-bank58/revision-i/run_patch58i.py --run-approved-patch-trial

The one trial is bounded to 30 seconds total, CPU2, conservative wrapper+child
1.5 GiB, source ≤200000 bytes and exactly two original PNGs. Each child has actual
wait4 exit/time/RSS evidence and before/after protected-input identities. No
automatic retry, source overwrite, next revision, four-root expansion or world
integration. Parent owns Git, CLOUD_RESUME and any external delivery.
