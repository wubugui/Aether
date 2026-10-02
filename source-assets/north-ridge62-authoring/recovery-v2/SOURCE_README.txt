North ridge62 isolated editable source

No Godot world is imported into this file. Source materials are a rock/grass/snow
form study, not lighting, weather, cloud occlusion or final reference acceptance.
167 instance support constraints remain unresolved. Integration is prohibited.

One R62_MASTER_CONTROL triangulation has 27 points: 12 fixed boundary points and
15 named relief points. Change a relief vertex's Z or its named semantic handle's
Z, then explicitly run the embedded REBUILD62.py Text. Editing both adds both
height differences. X/Y edits require a new frozen design/binding, and are rejected.
Exit Edit Mode on every ridge mesh before running the Text; otherwise the
rebuild rejects rather than reading stale edit data. All six ridge mesh objects
must keep identity transforms; edit the control vertices or handle Z instead. No auto-executing handlers
or drivers are installed. The explicit rebuild never
saves, renders or exports. Subsequent edits are not the frozen candidate anymore.

R62_MASTER_EVALUATED is the one shared derived surface. Its four tile objects
are deterministic subsets, with original face order retained and clockwise
Godot faces reversed to Blender CCW. They are not separately generated mountains.
All four objects have editable Grass/Rock/Snow material slots and per-face region
attributes, and all 27 barycentric control weight groups. Native original_world,
canonical_base_y and collar attributes aid editing; embedded BINDINGS62.json
retains exact full-precision weights, canonical original Y and source mappings.

Godot→Blender map: (worldX+2560, -worldZ-4608, worldY). Only local XZ origin shifts;
world Y is unchanged. The original before-XYZ and candidate-Y are float32-checked.
Every original tile triangle and corner maps to the shared source mesh. This is
verified original GPU index mapping from a narrow offline read of four source
ArrayMesh blocks. Derived meshes retain 6144/6144/6058/6009 original attribute
vertex slots and index ordering, original local XYZ and original RGBA data. The
original vertex/index/color packed bytes are archived in BINDINGS62.json. UV/UV2
are absent in all four original surfaces. Original packed normal/tangent bytes
are retained without claiming a new semantic decode or native Godot readback.
Future integration must preserve all untouched channels and source IDs.

1131 and 1347 retain original world eye/target/FOV55 at 1179×664. Side/back are
supplemental source geometry diagnostics. No world camera or weather is edited.
The entire current world, protected coasts/lake/cliff and all scattering remain
outside this source and unchanged. Existing terrain seam gaps are not repaired
except the explicitly proposed 73 shared changed sample positions.

Recovery-v2 execution note
The frozen design and its complete compact BINDINGS62.json bytes are unchanged.
BULK62.py is an additional internally packed editable helper. All native groups,
attributes, source slot mappings and normals remain real mesh data; batching does
not replace them with a recipe-only report. Text files are loaded into memory
with no retained external filepath. This is still a source form/material study,
not a world/weather/support/visual acceptance result.
