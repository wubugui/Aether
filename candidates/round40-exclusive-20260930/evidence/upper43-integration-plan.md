# Upper43 local candidate plan and findings

No Game43 build has been run. Await parent approval of clean graphical 42d serialization. No old scene, default scene, protected Blender master or remote branch was changed.

## Actual geometry

42c has 12 UpperCloudBank41 assemblies. Contrary to their names these are already the cloud_sea_41 assets, substituted in build_weather42b, each containing 20 mesh parts. Their nonuniform (2,1.1,1.4) scale produces ~3.3–3.9 km horizontal world AABBs and 0.57–0.63 km depth in Y. Existing upper43 GLBs each have 11 separate meshes; original local dimensions are 699–747 m X, 376–402 m Y, 410–448 m Z. See upper43-bounds-audit.json.

Game43 will preserve all 12 positions and orientations, replacing only UpperCloudBank41_* with UpperCloudBank43_* at uniform scale 2.0. The reduced footprint and true vertical proportions are explicit candidate design choices, not measured reference facts. The 25 sea placements, 56 distant banks, 31 World/Clouds placements, native coastal clouds, weather, terrain, ports, islands, interiors and cameras remain unchanged.

## Gray-slab attribution

Read-only exact mesh-triangle rays sampled 35 directions across the upper half of each absolute reference camera. This is geometric cloud-source attribution, excluding terrain occlusion, not final pixel attribution. 1343 hits 19 distant banks and one world cloud, zero upper clouds. 1128 hits 21 distant banks, zero upper clouds. Main first surfaces are DistantCloudBank41_-2_-3/-3_-3/-1_-3 for 1343 and DistantCloudBank41_-2_-4/-1_-3/0_-4 for 1128. Therefore upper43 is not claimed to repair the dominant daylight gray floor. The separate distant44 asset task owns that next defect. See cloud43-source-rays.json for exact paths and distances.

1216 does include upper clouds (3 hits), along with sea/distant/world; 1278 includes two upper hits. Upper changes require high-altitude, cabin and side/back validation.

## Native source visual QA

Blender 4.5.14 opened the retained .blend and rendered 9 CPU Cycles asset-only front/side/underside views, three variants. No source save was invoked; source SHA256 is identical before and after. See upper43-cpu-native-preview/report.json and contact-sheet.jpg. No planar base is present; visible rounded lobes continue underneath and have true side depth. Caveat: joined sphere-like clumps and repeated triangle facets remain evident. This is an improved candidate for integration comparison, not style acceptance, and is not a real Godot GPU result.

## Safety and testing

build_upper43.gd rejects headless and existing Game43 paths. It builds from Game42d without adding it to the scene tree, exports editable native prefabs, replaces only the exact 12 upper branches, then compares all unaffected node classes, script paths, transforms, mesh-face digests, concave collision-face digests and every MultiMesh buffer before, after mutation and after fresh disk reload. Rain/snow must retain 1800/1200 instances and 16 floats per instance. It does not change project.godot.

verify_upper43.gd defaults to focused original boot, 1343, 1128, 1216 front/side/back/translation and 1342 captures, plus temporary cloud-category isolation captures. Those diagnostic visibility changes are reverted and excluded from fidelity acceptance. --full retains inherited 42d regression and captures every current 20-entry reference plan front/side/back/translation plus all three cloud variants front/side/back/underside. Original assets/reference.jpg retains the separate boot identity, not a fabricated 21st plan entry. Hardware GPU acceptance and visual acceptance remain false in reports and are separate from functional test results.

All three GDScript tools parse using Godot 4.5.1. Graphical build and native viewport comparison remain pending. Software llvmpipe images may be useful diagnostics but cannot satisfy GOAL GPU/visual acceptance.
