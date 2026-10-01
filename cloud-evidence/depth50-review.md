# Game50: local geometric water-depth correction

2026-10-01 01:13 UTC. Saved candidate SHA256 `031b39ea75680e98fbed4882507251ec0ebfb3469300f82402891a0137351ff0`. Build/reload exit0 in `depth50-20261001T005643Z-gxCMO5`. Independent verifier v2 exit0 in `depth50-verify-v2-20261001T010738Z-G3enLm`: 227 bounded checks,60 actual PNG,12 poses with original49 → depth-disabled50 → restored49 → enabled50 → disabled50 controls. Every required full-RGBA comparison is zero difference, independently recomputed from saved PNGs. Two outward-looking outside-domain controls also have zero change with correction enabled. Mesa llvmpipe software renderer, official Godot4.5.1 Compatibility; hardware-GPU acceptance remains false.

## What changed

One saved geographic depth controller, five external R32F images, and the existing Ocean material binding. No geometry, collision, camera/layer, material-authority or reflection changes. Actual world-XZ signed support height replaces the incorrect screen-ray opaque hit as vertical water depth inside the lake domain. One-metre base plus four0.25m island patches, eight-metre patch feather and32m domain feather. All old shader styling/uniforms remain. Disabling the new path restores original49 rendered pixels exactly. Original scene graph outside the one binding,48,000 weather floats, input assets, protected cliff master and49 scene remain unchanged.

The depth grid is an approximation, not exact continuous geometry: signed sample values accurate to7.5e-6m do not imply equivalent continuous interpolation accuracy. Retained fusion evidence includes discontinuity outliers up to3.24m. Residual thin cyan edge on close island views remains; no claim every shoreline artifact is eliminated.

## Actual visual review

Developer directly viewed all12 enabled frames, original1128/1129 references, and original49 near-right comparison. Large cyan vertical blocks under islands disappear without moving or removing their physical roots. This is useful limited progress. Thin cyan edge remains near some rock lips. Bright triangular specular flashes also existed in49. Strong regular wave bands, missing mountain/island/airship reflections, oversized close rock-like clouds, simplistic mountains and green shoreline walls remain. Reference composition has a large close side-view airship and surrounding snowy mountains; current fixed shots still show a tiny distant head-on ship and materially different landforms. No reference is accepted by this checkpoint.

## Physics and first failed verifier

Original350m lateral camera-sphere tests still hit the same ground with exact49 safe fractions0.9931640625/0.55859375. Both150m lateral and200m approaches remain clear. This is not full-airship flight certification. During v2 freeze, all2,235 CollisionObject3D modes, layers, masks and RIDs remain unchanged. Same actual World3D used for every comparison.

The first verifier was manually interrupted after27 PNG because its freeze disabled CollisionObject3D processing modes, removing them from physics space, and its global uniform getter generated errors outside editor. Those motion results are INVALID. Original scripts/logs/images remain, with no invented exit code. v2 only stops callbacks and explicitly sets frozen time0.35; original failure is not overwritten. The successful v2 stderr contains only the known VSync warning.

## Status and next

Saved-state/runtime/normal-pass preservation gates pass within the stated scope. Requested-motion-all=false, total-acceptance=false, visual-acceptance=false, hardware-GPU=false. Independent reviewer could not be started due runtime thread limit; this is developer review, not independent acceptance. Game50 is an independent candidate, default project scene unchanged. Continue51 same-world native reflection with strict main-pass/material controls, then remaining geometry, weather, cabin and all-reference work. Git cloud write authentication remains unavailable; local commits and editable sources are preserved while existing manual transfer awaits the user's downloaded path.
