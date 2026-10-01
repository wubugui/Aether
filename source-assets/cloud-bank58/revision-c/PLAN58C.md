# 58C source proposal: hierarchy before construction

**Plan only. NoC mesh, Blender build, renderer, world or source-context image has
been run.** All57 controls below are authored design hypotheses, not measured
reference-world positions. A/B sources and all their real failed images remain
frozen. The B complete freeze is
`../revision-b-complete-freeze-20261001T1205Z.json`.

## What the actual reference shows

The original `ref/1216.png` (1672×941) was viewed again before this plan. The
following approximate pixel ranges describe overlapping bands and visible
silhouette scales; they are not automatic segmentation and do not recover real
world metres from the image.

| Layer | Approximate image area | Primary / medium / small apparent widths | Shape relationship |
|---|---|---|---|
| Near | y490…941, full width |150…400 /45…140 /10…45px | Thick irregular masses run beyond the frame. Medium shoulders and short folds carry a large share of visible structure. Downward bodies are unequal; no outer rim encloses a basin |
| Middle | y425…640 |45…140 /15…55 /4…20px | Short overlapping crowns, alternating heights and branching ridges. Dark valleys continue into structured cloud relief |
| Far horizon | roughlyx400…1672,y365…465 |8…35 /3…12 /1…5px | Dense small relief merges into bright horizontal bands. Equal large isolated spheres would destroy the depth progression |
| Upper layers | y35…410 |180…700px long, commonly10…55px thick; rare35…110px rises | Broad shallow horizontal bodies with occasional angular peaks and overlapping levels |

The reference has hard low-poly faces. It is not a collection of smooth white
balls, a mountainous rectangle, or a few smooth tubes around a depression. The
near bright/dark contrast is also a lighting and atmosphere problem: the bright
horizon, dark deep folds and lightning cannot be accepted through source shape
alone or faked by a material brightening pass.

## Four-root world sketch

`world-plan58c.svg` / `world-plan58c.png` is an editable schematic plan with actual
native root positions, original1216 camera and forward direction, all57 control
extents, two valley routes and three proposed cross-section planes. Its polygons
are control extent guides, not a cloud mesh, triangle coverage, or connection
proof. All native positions and rotations remain inherited from saved52f.

- CloudSea_0_0: (3200,700,3000)
- CloudSea_0_1: (3200,700,4150)
- CloudSea_1_0: (4350,700,3000)
- CloudSea_1_1: (4350,700,4150)

Original camera: (3000,1150,4300), horizontal forward approximately
(+0.7282,−0.6854) in worldXZ. The depth chart separates near<1050m, middle
1050…1900m and the local far end>1900m as an authored arrangement. This four-root
patch cannot establish the reference's full horizon;21 external roots and the
rest of the sky remain outside its current scope. This is still52f research,
not a source integration into coast56 or60.

## Planned native controls, not another11-loft ring

`control-plan58c.json` gives every control's unique ID, role, worldXYZ, extentXYZ,
yaw, parent form and intended construction. None may be mechanically repeated
across roots. The proposed count is9 lower density bodies,6 primary crowns,
18 medium folds and24 small local edge changes.

The lower9 are independently shaped compact unequal bodies, generally650…910m
wide,500…610m high and670…870m deep. They are staggered throughout the interior,
including the middle of the patch. They are not an enclosing boundary loop and
not a common bottom sheet. Each has a different side return and hanging belly;
their full3D overlap must establish solid lower density beneath intended valleys.
Exact connections remain unproved until actual mesh/ray checks.

Six short primary crowns organize the view: three near crowns(P01/P02/P03), two
middle crowns(P04/P05), and one smaller local far-edge crown(P06). Their horizontal
scales shrink from roughly490…590m near to350m at the far end. Heights and axes
differ. A native asymmetric faceted control volume must be shaped separately for
each; no kilometre-long equal-section tube, generic cone, or scaled sphere.

The18 medium folds are substantial shoulder/ledge volumes,160…300m horizontally,
with approximately130…200m height. They are placed on different sides and heights
of the primaries. They must remain clearly visible after union and simplification:
they are not decorative caps on one large underlying carrier.

The24 small folds are55…120m horizontally, generally50…95m high, concentrated at
specific shoulder edges and valley turns. OnlyS23/S24 are explicitly rare higher
angular lips. No even random scatter and no high cone at every crown. Small
features must not be used to disguise an incorrect large silhouette.

The existing three upper ribbons may be retained unchanged only as a comparison
constant in an initial source view. Their previous rejection status remains;
this proposal does not claim that three ribbons complete the reference sky.

## Real cloud floors: proof required after construction

V1 is a broken diagonal corridor throughL02/L03/L05/L06/L09, with a planned120m
wide test lane. V2 is a shorter transverse middle fold through the central bodies,
with a100m wide lane. Their first cloud surface targets are roughlyY460…790 and
Y460…780 respectively, below the primary relief, not at seaY0.

Once the actual source exists, cast vertical rays from worldY1500 through real
triangles at every25m station along each route and at transverse offsets−half
width,0,+half width. Record all ordered entry/exit hits, coordinates, triangle
IDs and closed-solid intervals. Every intended valley sample must intersect a
real cloud interval at least160m thick. Missing support, an unplanned through
slot or a cloud floor outside the intended band fails the design. AABB coverage,
convex-hull filling, implied heightfields or a later flat plate cannot satisfy it.

Intersect the final actual triangles with SCT1:worldZ3800, SCT2:worldX3800 and
SCT3:worldZ3100. Save the actual top/bottom contours and enclosed solid intervals
in each section. The section plots are diagnostics, not rendered beauty images.
For this dense local design, require a single orientable closed lower surface
with genus0, in addition to the existing zero boundary/nonmanifold/self-crossing
and positive-volume requirements. The two through handles ofB are explicitly
not intended inC. No topology gate may be relaxed to admit a modeling artifact.

The original camera must again be classified against real closed triangles.
That is only a point test, not full ship, camera sphere or swept flight clearance.
External21-root contact and inside/outside classification must accompany any
later source-context comparison. A sampled distance to old surfaces is not a
gap-width measurement or proof of a usable boundary.

## Order of work, if this source plan is accepted

1. Author the9 lower compact volumes and6 short primary masses as editable
   native3D controls. Check underside/outer silhouette and support before adding
   small details; no rectangle, oval tray, or enclosing ring may dominate
2. Add18 substantial shoulders and then24 localized edge changes. Preserve the
   design hierarchy through a bounded union operation. Keep native controls,
   before/after shells, exact input hashes and any failure artifacts
3. Actual rays/sections and topology gates first. If simplification is needed,
   keep the entire unsimplified shell and report volume and bidirectional sampled
   surface offsets. Counts and smoothness are not visual quality metrics
4. Five actual full-source faces with fixed neutral lighting and no crop. Reject
   long sausages, repeated caps, a carrier platform, empty long slots, or forms
   lacking medium scale before any context/world proposal

No construction or runtime entry is included in this plan. Parent review of the
reference breakdown and world/control layout precedes another source build.
