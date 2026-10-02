# K in the real Game61 world: four original images, rejected candidate

Actual run2026-10-02T12:18:54Z. Native Godot4.5.1, llvmpipe, CPU[0,1]. All four requested normal-material1179×664 PNGs were produced; the final restore gate failed and the overall run is rejected.

- ChildPID227195 exited1 in58.631302052s; wrapper exited1 in71.492864005s. No240s timeout or RSS stop, actual child peak1832760KiB/observed aggregate1869596KiB
- Original/K paired front420967/414964B, fixed side-back267170B, fixed near299361B. Original native report contains all4captures, camera/projection, native storage/material and sparse actual indexed-triangle rays
- Sole failing native check: `Opt-out and original observation camera restored`. Its expression combines enabled/old visibility/K visibility/global camera-transform equality; final individual terms and actual final camera matrix were not separately logged. Therefore the failure cannot yet be attributed solely to transform rounding or visibility
- Original wrapper stops at actual process failure before validate_images; its images:0 means that wrapper validation branch was never accepted, not that the four PNG files do not exist. Original reports and logs are retained unchanged
- Main project and all frozen inputs unchanged. No saved geometry/asset/export/import mutation. Original VSync-driver warning and restore error remain intact

## Actual visual review

Parent opened all four PNGs. The paired K view opens a large near-black gap on the lower-right where the much larger original cloud unit was removed. The small three-crown K is only partly exposed. The near image has a large nearly uniform dark angular face with a narrow bright cap, reading as a rigid crown/cardboard form rather than layered cloud volume; the side-back shows real lit thickness but substantial neighboring occlusion. This one-unit replacement is rejected for world scale, continuity and cloud-form appearance. It must not be rolled out to other roots.

The four-view evidence is still useful despite the final runtime gate failure. No threshold/report is changed, and no unchanged four-view rerun is planned. Next design must explicitly account for the original bank's much larger coverage and actual neighboring geometry, with a separately authored controlled layout rather than stretching/moving this K, hiding neighbors or changing the acceptance camera/weather. Independent review is a separate artifact when available.

Original four PNGs/native report/process/terminal are preserved. Full project and shared-copy manifests are lossless gzip with original sizes/SHA in storage.json. No image alteration, crop, composite, debug material or generated substitute is used. Full GOAL, flight, hardwareGPU and all cloud-world visual acceptance remain false.
