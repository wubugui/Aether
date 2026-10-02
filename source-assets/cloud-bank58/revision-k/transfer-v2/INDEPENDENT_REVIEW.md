# Independent transfer-v2 preparation review

2026-10-02: a separate read-only reviewer found no blocking defect in the new
normal-only transfer code. Normal and optimized Python each independently passed
12 test methods, including all 384 per-triangle winding reversals. Tests produced
only in-memory bytes; no adjusted GLB file or native process was created.

The reviewer independently assigned each restored normal directly from the
original source face/loop/vertex data, without using `assigned_normals`. All 1,152
mapped float32 normals matched bit-for-bit. The in-memory adjusted SHA is
`4aa51a731723cb6cadf7808da210c232ddae97a9026ab59fe08b9c3846817441`;
6,297 changed bytes lie entirely inside the 13,824 allowed NORMAL bytes. Every
other byte is unchanged. The unchanged original GLB geometry contract passes with
maximum normal component error `8.509929039557385e-6` and position error zero.

Reviewed checks include unique exact authored-position mapping, oriented triangle
bijection, actual source-corner ownership, rejected ambiguous shared normal slots,
normal accessor bounds/nonoverlap, immutable JSON/material/positions/indices,
actual capture SHA/PID/wait4/source binding, preservation of both prior failures,
original geometry/material gates, no-Blender/no-output default, one-shot admission,
native import/save/fresh-load protocol and source/input/main-project protection.

Material evidence is intentionally bounded: the actual source helper checks color
and roughness; metallic/culling expectations retain the original authoring/v1
contract rather than claiming a new native readback. The original GLB `3e-5`
normal tolerance remains unchanged; Godot separately keeps its pre-existing
v1 `2e-4` packed-normal allowance. Neither is newly relaxed.

The review approves preparation only. No Godot parse/import/save/reload result,
adjusted GLB on disk, world integration, image or visual acceptance is claimed.
The parent owns publication and future scheduling. Final manifest SHA checking
follows manifest creation and does not authorize launching.
