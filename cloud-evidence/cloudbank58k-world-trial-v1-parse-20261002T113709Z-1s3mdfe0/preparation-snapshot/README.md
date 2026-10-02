# One K unit in the existing Game61 world

Source preparation only. No engine, new asset or image has been generated here.
The source-bound native K asset passed saved/fresh reload in the separately
published cache-readback-v3 run. World suitability remains unaccepted.

## Exact placement and its known design risk

Current Game61Coast inherits Game60Observation → Game56Coast →
Game55Observation → the flattened Game53dWest. Its 25 CloudSea roots each contain
one original cloud46 continuous crown. The historical 52f intake's 125 parts are
not the current world's contents.

The explicitly chosen trial unit is
`SkyRegion39/CloudSea_1_1/cloud_sea_46_0_continuous_crown`, native mesh
`ArrayMesh_d78o4`, 14374 vertices and 15492 indices. It is the nearest of the four
original roots to the unchanged K anchor. This is a new bounded design choice,
not a historical claim that D/K specified this exact replacement.

K's existing relative coordinates already use world axes and absolute world Y.
It is attached under identity `SkyRegion39/CloudKTrial` with identity basis and
the single translation `(3958,0,3667)`. It does not inherit the old root's rotated
basis. No source UV frame, recenter, scale, extra altitude, or second translation
is applied. Old geometry is retained, with exactly one mesh's visibility toggled.
Default `enabled=false`; opt-out restores the original mesh and hides K.

Offline saved geometry bounds are approximately:

- Old unit: `(3634.751,533.419,3436.617)` to `(5078.773,1057.067,4925.965)`
- K: `(3724.555,606.329,3483.219)` to `(4184.941,851.983,3832.920)`
- Old X/Z spans 1444.023/1489.348 m; K spans 460.386/349.701 m, respectively
  31.882%/23.480%. K's XZ AABB area is only 7.486% of the original's

K's AABB lies inside the old unit's. Their AABB gap is zero; no minimum surface
distance or true boundary intersection is inferred from this. Removing that
large old unit may create an unacceptable gap. This experiment cannot be accepted
because the individual source is watertight, nor because its bounds are contained.

`placement-provenance.json` binds the actual fixed current resources and records
four relevant roots only. At original 1216 camera `(3000,1150,4300)`, FOV 62 and
1180×664, projected K vertex bounds are about `(557.89,380.71)` to
`(789.68,493.44)` px, depth 1064.92–1345.80 m. All vertices are in front.
Of 384 actual K face-centroid rays, 178 have no earlier K face; after replacing
only 1_1, 83 also have no earlier triangle in the three relevant neighbors.
This is a limited geometry sample set, not visible pixel area or all-world proof.
Neighbor 0_1 obstructs 209 total face-centroid segments and 1_0 obstructs 35;
their union is not the sum. These actual indexed-triangle diagnostics preserve
the neighboring geometry and do not claim a box hit is an occlusion.

## Material and reference inspection

The original 1216 reference and both actual K source PNGs have been opened and
inspected: the reference requires a layered cloud field with deep valleys,
lit crowns and storm undersides. K's front view shows one small three-crown
volume; the side/back reveals its closed, faceted underside. These source-only
images contain no other clouds, ship, world lighting or actual world occlusion.
They cannot prove that replacing the much larger existing bank is appropriate.

The native K material stays exactly as saved: opaque StandardMaterial3D,
albedo sRGB `(0.7735731,0.7977378,0.8378605,1)`, roughness `0.899999976`, metallic 0,
two-sided, no textures/emission. Its unoverridden diffuse default is Burley;
no vertex-color modulation is enabled. The old override is white
StandardMaterial3D, Lambert-wrap mode 2, with packed vertex colors supplying
density and roughness default 1.0. Both use native per-pixel lighting. The future
native report reads these settings explicitly for both, including fog and any
next pass, rather than interpreting missing serialized properties as new reads.

SceneEnvironment42b registers ShaderMaterial uniforms only. Standard materials
already receive the common native Sun, ambient, fog and spatial lightning in the
same World3D. Assigning the old white vertex-color override to K would change its
authored material, so the trial does not do so. No shader/material/weather source
is modified. The old `cloud_tint` reference field is not independently applied to
these StandardMaterial instances.

## Finite actual observation protocol

The prepared capture code loads one temporary copy of the actual Game61 world.
It uses inherited `observe_reference("1216")`, then the existing weather's
`seek_time(0)` and `seek_time(.35)` and freezes callbacks for reproducible static
observations. Reflection remains enabled and is refreshed for each capture.
No physical player flight or continuous orbit is claimed or repeated.

Exactly four original normal-material PNGs, requested window 1180×664, fixed 1216
weather. Prior native Game61 produced 1179×664 PNGs under its actual viewport
setup. Requested window, actual window, visible rectangle, content-scale size,
texture and PNG dimensions and real projection are recorded separately. The
wrapper checks actual PNG IHDR against native Image dimensions and the fixed
1179×664 pixel contract. Texture API metadata is not used as image dimensions;
the prior 52g-v2 diagnosis records metadata 831×468 for actual 1179×664 pixels.
Unprojected K vertices are explicitly viewport coordinates, not assumed PNG
pixel coordinates:

1. Original Game61 at the inherited original 1216 camera, trial disabled
2. Same exact camera and projection, only the single K replacement enabled
3. Fixed side/back diagnostic: cloud bounds center plus normalized
   `(0.7591154,0.2741250,-0.5904230)` × 900 m, looking at that center, FOV 62
4. Fixed near diagnostic: center plus normalized
   `(-0.7182465,0.1647742,0.6759967)` × 600 m, looking at that center, FOV 62

The latter directions derive from the previously saved source camera directions;
their perspective distances are explicitly new inspection choices, not a claim
to reproduce the source's orthographic side/back projection. They never replace
the original front acceptance view. Each PNG records actual camera/projection,
all projected K vertices, live material settings, actual indexed cloud triangle
rays, reference/time and SHA. Rays are sparse and cloud-only; actual pixel review
must identify ship, neighboring clouds and any other geometric occlusion.

Reject the candidate if the original front is buried, the removal opens a visible
hole, the lit cloud lacks the desired hierarchy, or side/back/near images reveal
bad overlap, an implausible underside or a detached small object. Do not make it
pass by moving its anchor, increasing its scale/height, hiding neighbors, changing
the reference camera/weather, or rolling it out to the other roots. A mismatch
requires a separate recorded layout proposal.

## Execution and limits

Default command performs no action. Only the parent may run the scheduled stages
after this preparation is frozen, reviewed and published:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/world-trial-v1/run_world58k.py --parse-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/world-trial-v1/run_world58k.py --run-approved-world-trial

Parse compiles the scripts and loads the inherited resource, at most 30 s.
Renderer is one child, at most 240 s; whole wrapper 300 s. CPU affinity two,
llvmpipe worker limit two, combined child+wrapper RSS 3 GiB. This separately
named world budget accounts for the latest completed Game61 083649Z child peak
2668516 KiB (about 2.545 GiB), exceeding the initially proposed 2.5 GiB aggregate;
it does not revise the historical 1.5 GiB asset readback experiment. The bounded
support file differs from its frozen prior only in the RSS constant. There is
no extension inside an active run.

The parse wrapper copies the existing project into one new `/tmp` tree, then copies the
existing proven K `.tscn` and the new trial scripts/template there. It does not
use hardlinks or symlinks, edit main entry, launch Blender, import/export a GLB,
save world geometry, or target any Game62 path. Full main-project identity is
compared to the successful v3 manifest before starting and after terminal exit.
The same-freeze successful parse is required for the renderer, which reuses that
exact manifest-bound work copy with no second copy or fallback recreation.
The temporary project is not a Git deliverable or another backup. Each mode is
one-shot; failures, partial PNGs, logs, wait4 status, inputs and final reports
remain evidence. Native parse, graphical execution and visual review are still
pending. No preparation test can mark those stages passed.
