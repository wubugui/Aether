# 52h B — one primary, raw-union control retained

Parent five-view entry (primary only by default):

    python /workspace/scratch/a29d03198654/Aether/source-assets/cloud-sea52h-revision-b/run_preview52h_b.py

Optional independent raw-union comparison: append `--raw`. Neither preview has been run by the source worker. Preview uses the existing source material, camera/light setup, official Blender, Cycles CPU two threads and five actual 900×640 views. It never saves the source or changes the world.

Native source: `cloud_sea52h_b.blend`.
Primary export: `cloud_sea_52h_b_main_v0.glb`.
Raw union export: `cloud_sea_52h_b_raw_union.glb`.

## Construction

The 48 authored points and three closed original cages from `../cloud-sea52h-revision-b-plan` are preserved exactly in the source. They create one large offset body, a rear oblique medium shoulder and a lower front shoulder, with different belly levels. No common base disk, subtracted trench, ellipsoid, repeated axial cross-section or world generator is used.

The raw union is an exact positive union of those cages. For the primary, each original cage receives a 12m, two-segment bevel only at dihedral turns over0.5rad BEFORE exact positive union. Its wide center faces and medium-scale silhouette changes remain. No global voxel remesh, smooth modifier, subdivision or QuadriFlow occurs. Native cleanup is limited to numerical degeneracies below0.0001m and coincident vertices below0.00001m.

Applying the bevel AFTER union failed: tiny Boolean intersection edges globally clamped the bevel and produced a zero-area triangle with many slivers. That complete source, exports, scripts and failed proof remain under `attempt-a-post-union-bevel/`. The current implementation rounds the original clean cage edges before they intersect.

Original `Cloud46 diffuse warm crown cool belly` and the prior per-face vertex-color height formula are retained. Lighting/exposure changes are not part of construction.

## Native checks

Both variants have one connected component, positive volume, zero boundary/nonmanifold edges, zero nonadjacent triangle intersections and zero-area triangles. Blender reopened the native file and imported each real GLB; all oriented triangles match the source, maximum vertex distance0m, raw axis-bounds error0m. All three original cages remain closed, manifold and coordinate-exact within float precision (<0.0001m).

- Raw union:77 vertices,150 triangles,696×509.600×385m,volume45,309,982.98m³
- Primary:354 vertices,704 triangles,678.611×498.868×381.676m,volume44,722,177.07m³
- Official background Blender with two threads:build1.09s,peak368,304KiB; native readback/check0.51s
- Five-camera projection preflight completed0; actual previews remain pending

Thin-triangle limitation is explicit: raw union has11 aspect>20 triangles (0.264% of surface area); the primary has64 (1.543%). Primary15 aspect>100 triangles cover0.077% of the surface. The original macro-face cages have none over20. `thin-triangle-diagnostic.json` retains measured edge/area ranges. This is not waived as visually harmless; source views must reveal whether the limited bevel/union creates visible strips. Global retopology was not substituted because it erased the intended medium-scale form in the previous attempt.

## Scope and evidence

`geometry52h-b.json`, `construction52h-b.json`, model/check process logs and `protected-sources52h-b.json` contain the proof. Old52e/52f/52g/52h sources, the cage plan, saved Game52f, project defaults and cliff master are SHA-protected and unchanged. `manifest52h-b.json` fixes the current source and entry files.

The previous52h five-view result remains rejected. This B source has not received actual five-view visual approval, is not integrated, and does not fix the old lower-cloud thickness/navigation failures. No world or GUI was launched during construction. The separately rejected54 world payload was not touched or retried through another route.
