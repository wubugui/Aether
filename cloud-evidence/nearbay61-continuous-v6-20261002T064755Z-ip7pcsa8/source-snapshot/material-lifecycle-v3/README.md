# Orbit61 material / fixture-lifecycle repair preparation

Prepared only. No Godot parse, synthetic run, world run, or visual acceptance is claimed by this source revision.

## Scope

- `visible_geometry61.gd` now uses `BaseMaterial3D.is_grow_enabled()`. Its internal classifier returns an explicit success dictionary. Empty/default, negative, nonnumeric, and nonfinite classifications fail closed rather than looking like zero displacement.
- `fixture_lifecycle61.gd` observes only pending deletions following the existing explicit fixture. It records queued node identities and geometry descendants whose ancestors are queued, then waits for actual invalidation and an empty queue snapshot. It requires an unchanged native photo/reference pause, is limited to eight process boundaries / 15 seconds, and never forces a free, pauses the world, or discards an inventory entry.
- Inventory entries retain path, instance ID, initial candidate bounds, and queued ancestry. Any post-baseline queued deletion, actual deletion, or tree departure remains a failure, including distant watched geometry. The verifier checks the full inventory and new-node classification before F2.
- Existing shadow/LOD checks, world resources, default scene and previous failure evidence are unchanged.

## Independent lightweight fixture

Once the parent authorizes the CPU window:

```
python source-assets/coast61-nearbay-orbit/material-lifecycle-v3/run_fixture.py --run
```

Without `--run`, the wrapper does not invoke Godot. The explicit run pins the official4.5.1 binary SHA, uses two-CPU affinity and private absolute XDG paths, kills at59seconds, and retains original logs, source snapshots, true exit code, peak RSS, input integrity and case-by-case results in a fresh evidence directory. It does not load Game61, read MultiMesh resources, render images or send input.

Cases cover null/grow-disabled/grow-positive/grow-negative materials, empty/default and nonfinite classification rejection, next-pass/billboard/unknown shader rejection; real queued-parent/geometry-child lifetime, an unchanged surviving fixture node, pause-guard refusal, valid post-drain baseline, queued/actual post-baseline deletion with retained identity, distant-deletion refusal and queued-new-node refusal. The empty-dictionary case models the VM failure return shape without deliberately emitting an engine error.

## Evidence and limits

The preceding renderer failure did not record the removed node's identity. A stale queued node entering the baseline is a source-supported hypothesis, not a proven identification. New observations must establish which nodes were actually queued and released; successful synthetic deletion handling does not establish Game61 behavior.

Godot4.5.1 primary source:
- [grow property and getter binding](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/resources/material.cpp#L3458-L3460)
- [GDScript default typed return after runtime error](https://github.com/godotengine/godot/blob/4.5.1-stable/modules/gdscript/gdscript_vm.cpp#L3684-L3688)
- [physics delete-queue flush](https://github.com/godotengine/godot/blob/4.5.1-stable/scene/main/scene_tree.cpp#L593-L608)
