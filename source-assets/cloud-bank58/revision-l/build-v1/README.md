# L build-v1: implementation preparation blocked before candidate construction

This item is **not ready for native build**. It contains a bounded real-interface feasibility investigation and the source-only authoring adapter started before that investigation found an incompatible constraint. No new candidate mesh, `.blend`, GLB, image, world edit, Blender/Godot invocation, or native parse was made. Parent review and complete GitHub publication/readback must precede any separate design revision or resumed preparation.

## Blocking fact

See `interface-feasibility.json` and `interface-feasibility.md` for reproducible original triangle identities and the exact limits of the calculation. The old selected cloud and `CloudSea_1_2` have a real lower/lower intersection segment, not just overlapping XZ masks. It runs approximately from world XYZ `(4397.824341,632.786680,4610.587745)` to `(4401.818582,633.200990,4603.325973)`. At its midpoint the selected vertical surface interval is approximately `[632.993835,933.760525]`, the neighbor interval `[632.993835,725.670254]`; the lower-envelope order switches across the line. It is well inside the old projected outer boundary, beyond the original 80 m threshold.

Keeping that original lower seam exactly therefore conflicts with the design's interior belly range Y560–630. This is a conflict between two unchanged requirements, not a self-granted edge exception. The old genus-1 topology itself is not the blocker: the design permits a recorded new genus-0 topology and filling internal gaps without filling external concave bays.

Two separate possible design decisions remain unchosen:

1. Preserve the real original lower seam and explicitly revise/define the bounded locked-interface region and its relationship to the original interior belly rule. This would require an explicit new design revision; the current 120 m / Y560–630 constraints remain binding
2. Release the old internal lower-interface surface identity while preserving the intended contact connectivity, then design and independently prove a controlled new contact with the unchanged neighbor. Existing contact cannot be claimed retained merely because projection still overlaps

Neither option is implemented. An internal seam is never renamed an external rim to bypass the current rule.

## What is here

- `interface-feasibility.*`: the bounded old selected/four-neighbor investigation and reproducible witness; no repeat of the archived nine-cloud survey or 52 design rays
- `candidate-status.json`: explicit missing/blocked candidate status; contains no geometry
- `input-bindings.json`: SHA/size identities, authoritative v2 plus bound v1, exact four original world-camera byte strings, the original Blender linear material and actual K Godot sRGB readback. Context-document identities are historical task-entry snapshots; only the parent updates progress
- `contract58l.py`: pure preliminary schema/topology/control-response checks. The tiny fixture path is never a native acceptance path. All real-candidate calls have an unconditional unresolved-spatial-gate rejection
- `native58l.py`: unfinished authoring adapter retained as source only. Its proposed one master/derived export, seven semantic controls, embedded reconstruction, native raw capture code have not been run, integrated, or validated in Blender; source views are not implemented
- `run58l.py`: default no-op and explicit blocked-stage refusal. No process can be launched by this item. Reuse of the existing K/north supervisor, full before/after protection, budgets, one-shot launch and raw/native validator integration remains unfinished and must be reviewed in a future preparation
- `test_*.py` and test logs: pure Python/AST/no-op/refusal/synthetic negative controls only. Syntax success is not Blender parsing, saved-source validation, contact acceptance, visual acceptance or hardware GPU evidence

## Run the bounded pure checks

From this directory:

    PYTHONDONTWRITEBYTECODE=1 python test_contract58l.py
    PYTHONDONTWRITEBYTECODE=1 python -O test_contract58l.py
    PYTHONDONTWRITEBYTECODE=1 python test_native58l.py
    PYTHONDONTWRITEBYTECODE=1 python -O test_native58l.py
    PYTHONDONTWRITEBYTECODE=1 python run58l.py

The last command must report no-op. Passing `--run-approved source` or `--run-approved views` must refuse, even with a claimed publication/scheduling release. No flag can override the actual design blocker. The future implementation must not silently remove this guard.

## Restoration and evidence limits

All files in this directory are plain source/text/JSON. The existing survey NPZ is reused at `cloud-evidence/cloudbank-next-footprint-checkpoint-20261002/survey-grids.npz`; if absent after checkout, use that already-published directory's `restore_grid.py`, then verify the existing SHA `33dd320034359f224d9fff0a5a9d43f1a51a5a770beaefefe6954c6c6b7c1615`. Do not re-run `survey.py`. Existing native K source is an input, never a new output or a deformable L master.

The author directly opened `ref/1216.png` and all four original K world PNGs before preparing this item: broad reference shoulders/thick valley volume and K's large uncovered right/lower region, narrow lit crown and broad dark wall were visibly distinct. These are existing images only. No new diagram or rendered game view was created.

No Git or Slack operation was performed by this worker. This package remains blocked until independently reviewed and externally saved; external saving does not itself resolve the design conflict or authorize a native run.
