# Game61 stationary orbit: first bounded preparation item

Prepared after reading CLOUD_RESUME dated2026-10-01 17:03 and local HEAD
1e7bf8ef6d35699c64fb78b731aefdb2a6561807. This item does not modify project
resources, the published211m flight, its1477 pinned inputs, or its images.
No Godot parsing or renderer execution has been performed during preparation.

## Deliberately bounded first item

The single initial fixture is(-3430,28,-3665), facing the old water route.
After F2, the ship remains anchored while native right-button and MouseMotion
events rotate the unchanged controller to orbit.x=2.6, PI and4.0 radians.
Four normal-material screenshots are requested: default, shoreline candidate,
and two further views of the same ship/world. No flight key is pressed. The
later50m corridor and approximately31m stop are design-only fields in plan.json.
The next item must independently add and check the moving ship/camera envelope.

Default command is read-only and starts no engine:

    python source-assets/coast61-nearbay-orbit/run_orbit61.py --static-only

Future parent-coordinated commands, not executed by this preparation:

    python source-assets/coast61-nearbay-orbit/run_orbit61.py --parse-only
    python source-assets/coast61-nearbay-orbit/run_orbit61.py --run-renderer

The wrapper snapshots source hashes and uses new isolated external XDG folders,
actual logs/exit codes and a fresh output directory. It cannot set pixel coverage
true: that requires independent inspection of the normal-material PNG pixels.
It also never reports GUI focus, hardware GPU or full-reference acceptance.

## Clearance and explicit limits

The harness samples AFTER every actual game _process, retaining actual camera
transforms and the complete consecutive displacement. It queues these segments
for the next main-thread physics callback, where it checks both endpoint overlaps
and the full swept near-plane enclosure. Queries include the player's layer2
and all other physical body layers. No camera segment is inferred from screenshots
or sparse physics-only positions. Source-frozen native smoothing must explain
each process position; native avoidance correction stops the sequence.

A separate PhysicsServer3D space holds query-only static visual geometry. Actual
ArrayMesh indices and vertex arrays feed ConcavePolygonShape3D directly, avoiding
the known Mesh.get_faces 0.1mm snapping path. All candidate MeshInstance3D and
visible MultiMesh instances are considered, including tree crowns and bushes.
Every shader's vertex assignments must be classified. Native cloud displacement
has a complete+/-9m local envelope; the ship has a conservative complete visible
envelope including full propeller revolution, flag movement and native bob.
An envelope intersection is a conservative obstruction, never proof of a pixel.

The550m half-extent domain contains the66.13m anchored camera radius and all
450m local screenshot rays. Distant geometry outside this domain cannot intersect
these finite queries. It does not prove unbounded horizon visibility. Hidden
geometry, cull masks, nearby transforms and visible instance counts are tracked;
unclassified geometry, material movement, new visible candidate or candidate
changes abort. The first implementation intentionally does not support arbitrary
skeletal deformation, particles, new animated nearby rotors, or unknown shaders.
Such a stop is retained evidence requiring a separately reviewed extension.
Distant new streamed meshes are classified and watched, but do not fail solely
because they exist outside the finite query domain.

The desired orbit preflight includes the arc sagitta between0.05rad points.
Actual smoothed process segments are still checked independently, including
settling before/after each event and capture. The screenshot's own process segment
must be audited before the next input. Sparse screen rays record the nearest
actual triangle or conservative animated envelope within450m; ship occlusion is
not excluded. Pixel acceptance remains false even if every ray is clear.

The official API contracts consulted for preparation are:
- https://docs.godotengine.org/en/4.5/classes/class_physicsserver3d.html
- https://docs.godotengine.org/en/4.5/classes/class_physicsdirectspacestate3d.html
- https://docs.godotengine.org/en/4.5/classes/class_camera3d.html
- https://docs.godotengine.org/en/4.5/classes/class_meshinstance3d.html

## Old corridor reuse is only a terrain subset

New START equals old START plus90.1387818866m of the exact old direction.
The new50m route with25m end padding occupies old longitudinal coordinates
[65.1387818866,165.1387818866], inside old[-25,241.3330765278], with identical
25m lateral padding. With unchanged bound native export and scene hashes, the
old continuous terrain/shape maximumY=-8 proof applies to that rectangle.
It does not prove runtime body clearance atY28, updated props, or the camera
orbit which extends far outside that rectangle. No old test is rerun.

## Review after execution

Preserve parse failures, runtime failures and incomplete captures. A0 success
requires continuous process audit, unchanged ship, all four actual image hashes,
released inputs and unchanged frozen sources. Independently open every PNG and
identify actual visible shoreline/trees/rocks/ship-side pixels before making a
visual-coverage claim. Successful stationary orbit is not a31m flight result.
