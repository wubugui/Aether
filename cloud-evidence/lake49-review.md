# Game49 native rocky pine islands checkpoint

2026-10-01 UTC. Candidate SHA52d13fcb7ea412d3a0fae2eedb1d0f9c369dbe06c0da320d786c26c97c475ec8. Actual official Godot4.5.1 Compatibility software-render run lake49-20260930T234925Z-pYs5Nx: build/reload0, fresh verifier0,42PNG (13baseline48+29candidate49),894 bounded checks. No additional motion regressions. Requested350m paths still fail, total/visual/hardware-GPU/full-flight acceptance false. No claim from functional counts of visual success.

## Real additions and preservation

Four independent editable Blender/GLB assemblies: near-left island, far-middle island, near-right island, foreground rock;199 mesh parts,8086triangles,7 modeled pines. Closed roots extend1.492–1.506m below actual lakebed; trees supported on actual island triangles. Root/shoulder closed-solid overlaps checked. Existing known-clear150m lateral/200m approach camera routes remain clear.48 terrain,500 affected-lake scatter, all other old nodes/materials, weather48000float buffers and original protected native master unchanged. Full original source and rejected drafts retained.

First launch stopped beforeGodot due relative wrapper self-copy path; retained as234519Z-R5LZui. First actual build234621Z-PDyl9p failed group-scope comparison: exactly496new subtree keys,0oldgroup removed or changed.348 failed native files archived, hash manifest retained. Fix normalizes ./ paths and separately verifies entire new subtree; deliberate oldWorld group mutation remains detectable. Successful rerun uses new evidence directory, never overwrote failure.

## Actual visual review: still rejected

Developer directly viewed all29candidate frames (front/side/back, matching protected routes,4near views and12orbit angles) plus source representative images. Two lake fixed views now have real rocky islands, foreground stone and sparse pines with true parallax. These are not reference-camera props: the same saved entities remain visible from every new orbit.

However pronounced cyan vertical blocks/bands surround all island/rock roots. Close orbit views make the artifact unmistakable; no island-water appearance is accepted. Near-left island remains separated from original shore by112.62m, whereas1129 reference left edge implies a connected/overlapping shore composition. Grass/rock tops remain simple, pine silhouettes and scale remain preliminary; mirror reflection, mountains, clouds, neighboring port/snow scenes still fail their references.

## Cyan-root diagnosis, not hidden geometry

Read-only actual scene ray/triangle measurements in reflection50-material-intake/root-depth-ray-probes.json show existing Ocean shader uses the screen-ray opaque hit's Y as though it were vertical depth at water XZ. At pixel(980,485), real vertical depth23.24m but shader sees2.317m from foreground root side15.02m away inXZ. Left-island pixel(200,435):23.68m real vs3.296m shader,40.99mXZ shift. This explains the shallow-cyan projected column; moving roots upward to hide it would create false floating assets and is rejected. Next diagnostic will compare actual world-XZ geometry-derived depth, then restore original material to establish pixel causality before candidate integration.

## Reflection feasibility evidence (separate primitive project)

The attached primitive diagnostic images are not game beauty shots. SameWorld3D mirrored-camera/SubViewport reflection follows camera/object motion. A deliberately submerged cube exposes bad un-clipped reflection; reflection-pass worldY clip removes70610yellow pixels. Same-shader off/on control preserves upper300rows exactly0changedpixels. Original failed/corrected images remain. NoGame50 exists from these primitive tests; actual scene material preservation, runtime overrides, clipping, performance and dynamic validation are outstanding.

## Next

Maintain49 as a bounded intermediate native asset candidate, not default/production. Work on actual geometric water-depth and dynamically rendered lake reflection in independent50, then continue shoreline/mountain/lighting/weather/artwork iteration. All20 references and original opening GOAL stay open. Cloud rendered pixels are llvmpipe, not hardwareGPU acceptance.
