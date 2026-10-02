# Independent preparation reviews

Reviewed 2026-10-02. Neither review started an engine or modified original files.

## Codec-model mathematics

A separate reviewer checked the positive-handed signed-oct16 bound, including the
otherwise easy-to-miss `1/32767` tangent bias, piecewise-fold continuity,
normalization amplification, float32 operation budgets, and one additional
normalization before the dot-product check. Its fixed result is
`PERP_EPS=0.00034205286850920414`, `UNIT_EPS=64*2^-24`.
The reviewer explicitly limits this to a codec-model-derived acceptance threshold,
not proof of an unobserved prequantization vector or engine insertion call.
The full argument and source link are preserved in `TANGENT_BOUND.md`.

## Native preparation code

A second reviewer inspected the new probe, guard, runner, original probe diff and
existing evidence. It independently ran normal and optimized Python, 11 tests
each (including 384 per-face winding reversals), all passed on stdout without
overwriting our logs. It found no blocker in the planned two small native processes.

The review confirmed the fixed V/N/T/I channel types/counts and complete records,
exact stored vertex/index SHA and format/counts, embedded save, distinct fresh PID,
all geometry/tangent/material/transform/AABB equality, original geometry/material
gates, float32 AABB position/size/end split with the old false-failure negative
control, `/tmp` scope, no-import/no-GLB/no-Blender flow, and full source/frozen-input/
main-project before/after protections.

README/check/freeze were completed after that code review and receive a final
manifest check separately. Source-only review does not constitute actual GDScript
parse, native save or fresh reload success. The parent owns publication and
subsequent scheduling; no native authorization is implied by this document.
