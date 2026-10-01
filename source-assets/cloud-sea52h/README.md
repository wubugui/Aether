# 52h single native main crown — five-face review pending

Source: `cloud_sea52h_main.blend`
Export: `cloud_sea_52h_main_v0.glb`

This is one independent prototype. The failed 52g sources, original 52e/52f sources, saved world, material authority, and project default are unchanged. This is not a replacement scene or a visual acceptance.

The reference `ref/1216.png` was actually inspected again before construction. The shape starts from one irregular 63-vertex closed polyhedral cage with a broad offset main mass, an oblique medium shoulder, a lower small shoulder, and one through-going saddle line. Its 106 faces are not repeated axial sections. No ellipsoid primitive, Boolean cutter, spherical noise field, or light/exposure change is used. The cage has editable region vertex groups and a native 30m, three-segment macro-edge bevel modifier. A second full continuous editable volume is retained before final retopology. Four empties identify the three region groups and saddle route.

The finished shape follows a 6m native voxel surface and five local relaxation steps, then native Quadriflow retopology and beauty triangulation. This retains the large control-face directions while avoiding collapse decimation's thin triangles. The actual five-face renders must determine whether those directions read as clouds; topology checks do not establish this.

Actual final bounds: Blender (-689.804,-619.294,-34.958) to (-18.230,-120.743,321.415), dimensions 671.574 × 498.550 × 356.373m. This is smaller than the approximate 740×550m design envelope after round transitions and retopology; it was not scaled back out just to match the design numbers. Volume is 45,434,647.59m³. Placement is baked into vertices, object transforms remain identity. Original mapping stays Blender (x,y,z) → glTF/Godot (x,z,-y).

Inherited material `Cloud46 diffuse warm crown cool belly` is appended unchanged. Corner colors retain the existing height formula: v=.76+.16*clamp((z+190)/460,0,1), linear=((v+.055)/1.055)^2.4. Preview uses the same source lighting and exposure setup as the prior single-main comparisons.

## Checks completed without rendering

- 969 vertices, 1934 triangles, one connected component, positive volume
- Boundary edges 0, nonmanifold edges 0, nonadjacent triangle intersections 0, zero-area triangles 0
- Triangle aspect >20: 0; maximum 2.473
- Both editable mesh controls closed and manifold, positive volume
- Native Blender source reopened; GLB imported natively and every oriented triangle mapped exactly to the final source, maximum vertex distance 0m
- Raw GLB axis-bounds error 0; POSITION/NORMAL/COLOR_0 retained
- Official Blender 4.5.14, background, two threads: modeling 2.81s / 418,556KiB peak; native geometry/readback 0.77s / 269,884KiB
- Five-camera projection preflight completed 0, minimum border margin 0.153. No Cycles, GUI, or complete world was run by the source worker

The first source attempt is retained under `attempt-a-control-topology/`: the final was closed but the coarse control cage was nonmanifold at concave boundary triangulation, and collapse simplification created 83 thin triangles. The current cage explicitly clips its Delaunay roof/belly to the authored boundary and verifies every edge has two incident faces. Native quad retopology replaces that failed simplification. The original failed assets/reports remain unchanged.

## Parent-owned preview entry

    python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52h/run_preview_main52h.py

This schedules five actual source views (front/back/side/underside/top), 900×640, original source material. It uses official Blender in a parent-scheduled graphics window, Cycles CPU with two threads and 20 samples, and never saves the source. Evidence goes to a unique `cloud-evidence/cloudsea52h-main-source-v0-*` directory. Inputs, protected source/world hashes, logs, process exit code, five actual PNG dimensions/hashes and output hashes are retained. Hardware GPU and visual acceptance remain false.

The five-face preview has only been prepared. Do not expand variants or write a world until actual images are reviewed. The old two low bodies and their thick belly/navigation failures are not changed or claimed solved by this upper-main prototype.
