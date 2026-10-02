# K normal readback v1: preparation only

No native process has run. This package prepares **one** read-only Blender 4.5.14
open of the accepted 136,389-byte source, SHA256
`16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee`.
The first GLB export failed the unchanged normal gate. Its raw GLB and all original
code/evidence remain immutable. The independent diagnosis is at
`cloud-evidence/cloudbank58k-normal-diagnosis-20261002/`.

## Narrow future execution

Only after the parent schedules an exclusive native window:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/cloud-bank58/revision-k/normal-readback-v1/run_readback58k.py --run-approved-normal-readback`

Without the flag the runner prints preparation status and creates nothing.
Exclusive persistent attempt and terminal markers prohibit accidental reruns.
The native child has at most **30 seconds, two CPUs/threads, 1.5 GiB aggregate RSS**.
The complete wrapper, including full project hashing, has a 60-second alarm.
The unchanged audited import-v1 helper owns the PID and uses wait4 with kill/reap
on timeout, interruption or RSS overflow. Failed data and reports are retained.

The child performs only `bpy.ops.wm.open_mainfile` with autoexec disabled. It reads:

- Complete accepted native identity and dependencies before/after, original light
  and material checks, camera matrices/projections/resolution/aspect read directly
  and matched to the accepted report; exact `.blend` SHA before and after
- Exact 194 positions/384 triangles and accepted saved-array fingerprints
- 384 actual polygon normals, 1,152 corner normals, polygon loop lists, loop vertex
  IDs and loop-to-polygon owners, with exact float32 values

Actual arrays are written before the normal validation, so a numerical failure
cannot discard them again. A separate final native result binds that raw file's
SHA, native PID and validation. The wrapper revalidates the raw data independently
and binds the native result to wait4. All original preparation/protected hashes,
new preparation hashes, accepted source and every main-project file (including
`.godot`/`.import`) are verified before/after. The source is never saved; no export,
Godot, render, viewport, image, world or GLB adjustment is performed.

Independent review caught that the legacy camera-projection helper assigns the
active camera and render settings. The new collector does not call it. It reads
camera matrices and calculates projection with explicit stored resolution/aspect,
without property assignment. It additionally captures and compares the active
camera plus all five relevant render fields before/after. No old helper is changed.

The pure guard keeps the original `3e-5` unit/outward gate and exact native
polygon-to-corner equality. It must also reproduce every normal in the already
failed GLB with the installed exporter round(4)/normalize/Y-up operations, exactly.
A numerical mismatch remains a failed diagnostic with the actual arrays preserved.
This collection cannot declare transfer or visual acceptance.

Pure tests use explicitly simulated Newell normals, not claimed native values.
They cover identity/PID/scope, geometry corruption, all 384 flipped face normals,
loop mapping, NaN/infinity, float32 integrity, original tolerances, default no-launch
and the collector's sole allowed Blender operator. Normal and optimized runs are
saved separately. An independent review and frozen SHA manifest precede admission.
