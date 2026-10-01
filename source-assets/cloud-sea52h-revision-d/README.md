# 52h revision D: a continuous curved density volume

Status: native geometry/readback and camera framing checks pass; actual five-view appearance is pending. No rendering or world trial has been started by this source worker. C and its rejected five-view evidence are preserved. The proposed C runtime comparison was canceled before any runtime files were created or any world process started.

C's observed failure was a dominant planar stone shell with attached ledges. D contains none of that old shell geometry. Nine editable native Blender Metaball elements jointly form one continuous positive density surface: a large offset core, a broad medium rear shoulder, a low small front shoulder, and six differently oriented short rises. Density sums continuously across the joints instead of creating exact Boolean intersection creases. No bevel, negative cutter, random noise or Smooth modifier is used. Native quad remeshing and triangulation provide the restrained final facets.

The density elements use ELLIPSOID primitives as a modeling basis. Their combined outline is still subject to visual rejection if it reads as repetitive balls or a monotonous potato. Using continuous curved primitives does not itself demonstrate the desired cloud hierarchy.

## Editable construction

cloud_sea52h_d.blend contains CONTROL52hD_density, with nine individually editable native elements, per-element role labels and recorded centers, dimensions, rotations and stiffness; CONTROL52hD_continuous_density_skin preserves the converted skin before retopology. The final crown is a separate closed mesh. construction52h-d.json records the exact recipe and single uniform normalization used to retain the previous overall width. No C source mesh is loaded.

The native geometry has 919 vertices and 1834 triangles, one connected component, and zero boundary/nonmanifold edges, detected nonadjacent intersections or zero-area faces. Maximum triangle aspect is 2.780, with none above 20. The continuous pre-retopology control is also closed and self-intersection checks pass. All nine density elements reopen with the recorded type, center, radius, anisotropic size, quaternion rotation and stiffness; density threshold and overall placement/scale also match. The exported GLB returns the exact oriented triangles and vertices, with 0 m axis/vertex error.

Final bounds are [-709.600,-602.105,-25.743] to [-14.065,-79.043,364.982] in Blender coordinates, dimensions 695.535 × 523.063 × 390.724 m. Volume is 60,997,291.18 m³, 36.546% above C despite similar outer dimensions. The interior is fuller because the old cut corners and planar flanks were replaced with broad curvature. This is a material geometry change and may make the belly too heavy; it does not solve the known low-altitude cloud interiors/navigation problem.

The previous material and per-face vertex color are inherited exactly: v=.76+.16*clamp((z+190)/460,0,1), linear=((v+.055)/1.055)**2.4. Exposure and preview lighting were not altered.

Build: two CPU threads, 1.807 s, peak RSS 450,736 KiB. All prior source files, fixed Game52f, project.godot and cliff master are byte unchanged. The model build's default-extension cache emits a nonfatal readonly-config warning; all build/export/readback operations complete successfully.

## Five-view entry for parent scheduling

    python source-assets/cloud-sea52h-revision-d/run_preview52h_d.py

One source crown, five actual views, CPU two threads, established light/camera/material, 900 × 640, twenty samples, unique evidence directory, no source save. The camera-only preflight has minimum normalized margin 14.533%.

A separate geometric curvature diagnostic is in cloud-evidence/cloudsea52h-d-curvature-preflight-20261001T0952Z/connected-near-planar-patches.json. Its largest connected final-triangle patch staying within 2° of one seed normal falls from C's 16,281 m² (2.098% surface) to D's 2,765 m² (0.314%). This specifically checks reduction of broad near-planar regions. It is not a visual acceptance metric, and does not prove cloud likeness or resolve the larger belly volume.
