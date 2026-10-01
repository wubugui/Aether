# 52h revision C: eight uneven medium shoulders

Status: source geometry and Blender/GLB readback passed; five-view visual review pending. No render or world trial was started by the source worker. The rejected B source and its five images are preserved.

The actual pixels in ref/1216.png and all five B preview images were inspected. B removes the old long U-trench, but its three giant planar blocks and narrow continuous bevel strip read as manufactured stones. C retains the offset main/medium/small masses and differing bellies, lowers ten old roof vertices by 6–25 m, then adds eight short, unequally directed polyhedral shoulders. The concrete positions, full vertex data, rotations and macro edits are in plan52h-c.json.

The positive shoulder control boxes range from 75 to 170 m in width. Five interrupt the main crown's front, top, outer side and back; two belong to the medium mass, and one belongs to the low small mass. They overlap their parent volumes deeply. Control exposure beyond the adjusted parent's convex hull measures 25.5–72.0 m. This is geometric evidence that the added cages are not fully hidden; it is not proof that the final rendered shoulders read well.

Construction uses native Blender exact positive union, a 10 m voxel surface and two Smooth passes at factor 0.5 over the sampled surface to remove voxel steps, followed by native QuadriFlow and restrained triangulation. There is no bevel modifier, spherical primitive, subtractive cutter, repeated longitudinal section or random noise. Two local-neighborhood smoothing passes are explicitly retained in the recipe; no claim is made that all original sharp corners are preserved.

## Editable source

- cloud_sea52h_c.blend: 11 editable positive cages, exact pre-remesh union, continuous pre-retopology surface, and one final mesh
- cloud_sea_52h_c_main_v0.glb: the final crown only
- make_plan52h_c.py and model52h_c.py: exact reconstruction recipe; builder refuses to overwrite an existing blend
- geometry52h-c.json and intermediate-controls52h-c.json: native verification
- protected-sources52h-c.json: every file in earlier source stages hashed unchanged, plus fixed Game52f, project.godot and cliff master

The final crown is one continuous closed component, 938 vertices / 1872 triangles, with zero boundary/nonmanifold edges, nonadjacent triangle intersections and zero-area faces. Maximum triangle aspect is 3.503; none exceed 20. All eleven editing cages and both intermediate continuous bodies are also closed and free of detected self-intersections. GLB import returns the exact oriented triangle multiset and positions (maximum error 0); (x,y,z) to (x,z,-y) bounds error is 0.

Dimensions: 681.661 × 512.942 × 394.013 m. Volume: 44,671,766.17 m³, approximately 0.113% below B. The upper new shoulders therefore redistribute the existing scale rather than enlarge the whole asset substantially. Old material and vertex-color formula are retained without exposure edits.

Build used two CPU threads, 1.82 s and 445,320 KiB peak RSS. The first build emitted a nonfatal Blender extension-cache write warning for its default readonly config directory; source build/export/reopen succeeded. Verification and camera preflight use an explicit writable isolated config. No renderer was invoked in those checks.

## Parent-scheduled five-view entry

Run from the Aether workspace:

    python source-assets/cloud-sea52h-revision-c/run_preview52h_c.py

This renders exactly one source crown, front/side/back/top/underside, CPU two threads, 900 × 640, twenty samples, using the established source-preview lighting and unchanged material. It saves to a unique cloud-evidence/cloudsea52h-c-source-v0-* directory and never saves the source. All five camera preflights pass with minimum margin 15.805%. No B raw preview is included.

The five actual views must still decide whether the medium shoulders interrupt the giant facets sufficiently, whether transitions read as clouds rather than attached stones, and whether the old three-mass hierarchy remains clear. Geometry checks do not answer those questions. No world integration is authorized by this artifact.
