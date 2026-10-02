# K cache-only native roundtrip v3: preparation only

No engine or native parse has run. No new GLB, SCN or TSCN has been generated.
This package uses the **already imported native scene** from transfer-v2:

`cloud-evidence/cloudbank58k-transfer-v2-20261002T094351Z-egb4wx8d/imported-cache/cloud58k-native-import.scn`

11,096 bytes, SHA256
`1b94f241fba9cc48a7879ec71dee4ecff3854955be37f344158494997d3c3e42`.
The original raw/adjusted GLBs, accepted `.blend`, v1/v2 preparation and every
failed native result stay unchanged. No new export, GLB derivation or editor
import is included. The accepted editable source remains SHA256
`16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee`.

## Actual issue and narrow correction

The v2 editor imported successfully. Its subsequent old probe rejected an actual
TANGENT channel before saving or reloading. Offline diagnosis proves this exact
cache has only VERTEX/NORMAL/TANGENT/INDEX, format `34359742471`, 1,152 vertices and
1,152 indices. It is not nonindexed and has no UV/color/custom/skin data. See the
frozen `cloud-evidence/cloudbank58k-import-channel-diagnosis-20261002` evidence.

The new probe permits **only those four channels in this fixed cache**. It records
all channel types/counts, complete geometry and tangents before semantic failure
can stop it. Actual stored surface format/counts and the entire original vertex
and index byte hashes must match the preserved cache exactly. No additional
attribute, skin, blend-shape, bone or LOD payload is allowed. Same-face tangents
must remain bit-equal, as in the saved cache.

All 4,608 tangent components must be finite, unit direction plus handedness +1.
Direction orthogonality uses the signed-oct16/float32-derived bound in
`TANGENT_BOUND.md`, not a tolerance fitted to the measured maximum. Actual N and T
are normalized once for that dot test. The probe and independent Python wrapper
both check it. The exact prequantization direction and insertion call remain
unproved; previously denied source downloads are not retried.

The **unchanged original** geometry and material contracts still check authored
position mapping (`1e-5`), all oriented triangles, flat normals (`1e-7`), Godot
outward/unit normals (`2e-4`), bounds from actual vertices, neutral material/color
conversion/culling, no shader/texture/normal map/emission and identity transforms.
No world or camera is instantiated into a viewport and no image is taken.

## Native AABB representation, no epsilon increase

The actual saved AABB stores position and float32 size. Its Z endpoint from
float32(position+size) is `165.92007446289062`; actual maximum vertex Z is
`165.92005920410156`. The exact difference `1.52587890625e-5` would fail the old
endpoint-versus-vertex `1e-5` comparison even though every vertex is unchanged.

The new guard separately requires exact AABB position=min(vertices),
size=float32(max(vertices)-min(vertices)), and end=float32(position+size).
It also matches the original saved position/size/hash exactly. The actual vertex
position/bounds contract is unchanged, and no AABB epsilon is introduced. A test
retains the old comparison's explicit failing numerical result and rejects altered
position/size/end values rather than increasing its tolerance.

## One future two-process execution

Only after parent scheduling:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/cache-readback-v3/run_cache58k.py --run-approved-cache-readback`

The default prints preparation status and creates nothing. An exclusive one-shot
marker prevents concurrent/repeated runs over the original result. The runner
copies the already preserved native scene into a fresh minimal `/tmp` project,
with the new probe and project settings. It never launches the editor importer.

1. One headless resource-only read of `imported.scn`, then native PackedScene save
   with embedded duplicated resources: at most 20 seconds
2. A separate fresh process reloads `roundtrip.tscn`: at most 20 seconds

All native arrays **including tangents**, channel inventories, format, packed
surface hashes, materials, transforms and AABB forms must be exactly equal on the
fresh reload. Both snapshots must have no external dependencies. Native JSON uses
explicit full precision. All earlier artifacts remain hash-frozen between stages.

The wrapper retains the original 120-second total including full main-project
hashes, CPU2/thread2 and 1.5 GiB aggregate RSS guards, actual wait4/PID binding,
kill/reap and explicit terminal reports. Every main-project file including caches
and import sidecars is hashed before/after. The source/frozen inputs are protected.
Only scratch-native output is saved; `.blend`/main project/old attempts are not.

## Preparation evidence

Pure saved-data fixtures cover original geometry/material checks, all 384 triangle
reversals, exact storage hashes, forbidden channels/types, tangent finite/unit/
handedness/perpendicular bounds, exact AABB arithmetic plus the old failure, and
no-launch/no-copy/no-derivation defaults. An initial source-text assertion used
double quotes while the actual Python list used single quotes; its failure log is
retained and the test was corrected. No native failure is reclassified.

Preparation tests and review do not constitute native parse/read/save/reload,
transfer completion, world integration or visual acceptance. The final frozen
manifest and independent check must pass before scheduling.
