# Input-unit correction: focused engine checks passed

2026-10-02 04:34 UTC. No world run or image was produced by this item.

- [Actual native fixture](../../../../cloud-evidence/nearbay61-input-units-v5-20261002T043347Z-oqgvynhg/result.json): 43/43 checks passed, child/wrapper exit 0, 0.530 seconds, peak 119764KiB, CPU affinity [0,1], 19-second watchdog not triggered
- [Main check-only parse](../../../../cloud-evidence/nearbay61-orbit-parse-20261002T043356Z-3h274pae/wrapper-report.json): visible geometry and main entry both exit 0, 0.504/0.256 seconds, no timeout; the main preload includes the new native mouse helper
- No engine errors/leaks; complete raw logs, source snapshots, shell terminal output and input/evidence hashes retained in both new directories
- 1567 fixture-protected files unchanged, including all four saved world failure directories; all six fixture sources unchanged. Main parse's 1487-input manifest is identical before/after

## What was actually demonstrated

Godot4.5.1 headless root Window canvas_items scaling produced the live matrix
x=(0.7051435113,0), y=(0,0.7056323290), origin=(1,0).
The harness read that matrix rather than deriving a viewport/window ratio.
For intended local relative (-12.5,0), it sent (-8.8142938614,0);
the actual independent Node._input witness received (-12.5,0), once, with right
button held. The synthetic sink's unchanged game arithmetic applied
0.0500000007451 radians, inside the original 0.00001-radian bound.

With additional real root shear/translation, sent relative
(-7.0514349940,-0.8820404410) arrived as (-12.4999990463,0), once;
the angular increment remained within the same bound. Both cases proved native
parse/flush dispatch, not just algebra. Before/witness/after matrix and dimension
snapshots matched. Mouse position also returned to the intended logical center.

Actual InputEventMouseMotion.xformed_by tests covered identity, uniform,
nonuniform+translation, shear+translation, and reflection. Nonfinite/singular
input mappings were rejected. The production helper rejected missing/duplicate
receipt, the old wrong-unit delta, before/after and witness matrix changes, and
unheld-button state.

## Limits

This fixture has no game scene, physics/world, rendered pixels or real display.
The headless DisplayServer reports (0,0); its texture-size API reported
(832,469), not a physical captured image. These values are retained as reported,
not described as real display/PNG dimensions. The live matrix above belongs
only to this new fixture and is not retroactively assigned to the failed world.

The project game.gd, project.godot, assets, STEP_RADIANS=.05, native sensitivity,
original angular tolerance, hidden-geometry and physics gates remain unchanged.
A parent-coordinated new real world run must still record its own matrix,
received event and unchanged game increment before orbit/camera acceptance.
