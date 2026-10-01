# D native source and independent readback completed

2026-10-01 16:20 UTC. This small native-source item passed. It does not include
rendering or cloud-shape acceptance. The source remains an isolated reconstructed
fold junction, with the original 325 vertices / 646 triangles and full underside.

`fold58d.blend` is 114,775 bytes, natively compressed, with SHA256:

`2b742986751183db994b5d803127c45eb44a02046cd85a17f689355d1c2540a2`

Run: `cloud-evidence/cloudbank58d-native-20261001T162033Z-y035f3f3`.
Build child exit 0, new readback child exit 0, wrapper exit 0. Total 2.072303
seconds; actual peak child RSS 262,260 KiB. Both stderr logs are empty. Blender
4.5.14 binary SHA matched the official-restoration identity before startup.

## Stored source result

- One editable mesh, 34 unbeveled 3D POLY guides, 55 mesh edit groups, five
  cameras, one sun, one untextured neutral Principled material; no images or
  external linked libraries. The curves are guides, not mesh deformation
- Exact expected float32 vertex arrays and ordered oriented faces; identity
  object transform, retained input SHA and coordinate origin, no modifiers,
  all faces flat shaded. Maximum original world-coordinate error 0.00002999222 m
- One closed, consistently wound, orientable genus-zero shell, Euler 2,
  signed volume 113,624,980.626845 cubic metres. All 4,439 actual triangle
  candidates checked, including adjacent pairs; zero improper intersections
- All original valley samples pass: Vd 36/36, minimum solid thickness
  222.340401 m; Vback 18/18, minimum 237.616591 m. Original 25 m spacing,
  three lanes, 160 m minimum thickness and floor-height bands preserved
- All guide knots and stored width/junction metadata match. Every upper,
  side-ring and ROLE edit-group vertex index and weight matches exactly
- Main mesh is effectively visible through its object, collection and view
  layer. All guide objects and their collection are excluded from rendering
- Material contains only Principled BSDF → Material Output, no image or
  environment texture nodes, no packed images
- Original 1216 camera location matches exactly; maximum basis error is
  1.043082e-7 and projection matrix error 3.552714e-15. All five saved camera
  matrices are exact after reopening
- Full back, side, underside and top cameras frame all actual source vertices
  with minimum margins 0.089999914, 0.089999914, 0.089999959 and 0.089999974
- All frozen static D files, 293 frozen C files and this run's inputs retain SHA

The front remains the real reference camera. The actual stored input vertex
projection reaches reference pixel Y=1061.61, beyond the 941-pixel frame, so the
full underside must be evaluated in the other views. Vertex extrema are not a
visible silhouette or proof of appearance.

The first preparation-only syntax check found a missing closing parenthesis
before any Blender startup. The exact failed line, input SHA and one-character
fix are retained in `preparation-syntax-failure.json`. No native geometry stage
failed, and no geometry correction was made to obtain this result.

## Evidence and publication boundary

`outputs/fresh-readback58d.json` in the run contains the actual stored arrays'
topology and triangle contact results, all valley hits, curve/group identities,
visibility, material nodes and camera matrices. `process-report.json`,
`terminal-proof.json` and `wrapper.exit-code` establish the terminal result.
Input identities remain under `inputs/`, without duplicate asset snapshots.

`native-freeze58d-20261001T1620Z.json` binds the minimal native files and actual
run evidence. It excludes parent-owned CLOUD_RESUME and publication receipts.
Git publication is handled separately by the parent; this report alone does
not claim remote delivery.

The next small item, after this native result is published, is five actual
isolated source images. No PNG, GLB or world integration was produced here.
Sampled geometry cannot establish continuous valley-band or ship-path clearance,
and D still has no visual pass.
