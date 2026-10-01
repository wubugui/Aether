# Next lake spatial observations

This is a proposal, not an implementation or an acceptance claim. Saved51b, its original1128/1129 observations, all terrain, waterY0 and all camera fields remain unchanged.

## What the actual reference images require

Re-inspected `ref/1128.png` and `ref/1129.png`: the large airship sits to the right in broadside view; snow-covered mountain masses occupy both outer sides with a low central opening; cloud bands frame a large open center.1129 adds a connected near-left shore, a separate right pine island and near-left rock. Current mirrored water does not by itself establish these shapes or their spatial relationships. The49 near-left island is still separate from the mainland, and that known mismatch remains.

## Preserve the original controls, then label any calibration separately

The original camera data points upward:1128 is about5.36degrees,1129 about4.36degrees. With the actual KEEP_HEIGHT camera policy, a horizontalY0 plane has its infinite horizon at approximately57.5% and55.9% of image height. The reference lake/mountain-foot transition is visually around48–50%. Changing only mountain meshes cannot raise the infiniteY0-plane horizon above the center for these upward-looking cameras. Reference-foot placement is an approximate visual estimate, not a recovered camera calibration.

`camera-geometry.json` records exact source camera/airship settings, the sourceSHA and the analytical horizon calculation. A separate diagnostic observation could keep each camera position, yaw andFOV while testing a slight downward pitch, for example−1.5degrees. This produces a horizon near48% and allows the hypothesis to be tested. Its images must carry a new diagnostic label and appear alongside the unchanged original1128/1129 controls; they must never replace them silently.

## Airship framing and model shape are separate problems

The current observation settings are1128 distance120m/right0/yaw1.6 and1129 distance85m/right12/yaw1.7. The ship's long axis is approximatelyX, so these yaw values present an end-on silhouette to the lake camera. A side-on yaw/nearer placement is a useful independent observation before altering the model.

The existing ready49 mesh audit gives118 visual mesh bounds: before-ready whole-ship worldAABB approximately15.93×15.75×9.61m; its Envelope AABB approximately14.02×8.32×9.05m. That audit uses a rotated ship, so horizontal dimensions are only broadside estimates; vertical height is unaffected by yaw. Saved51b preserves this geometry. The reference envelope appears more elongated than this existing balloon. Do not assume yaw alone will solve its proportions, and do not stretch the global model without a native-source and collider review.

## Suggested first geometry review after reflection/motion evidence

1. Review a near-side airship diagnostic at the original lake cameras to separate yaw/distance from envelope and gondola proportion errors. Keep the saved model unchanged for this observation.
2. Establish left/right snow-mass silhouettes and a low central opening in the actual lake geography. Use editable native meshes, maintain the open water route and protected neighboring work, and inspect both fixed1128/1129 cameras plus side/back views. Avoid replacing the issue with a snow color change on the small central peak cluster.
3. Treat cloud distance and spatial distribution as a separate world-layout edit: broad distant bands and open central sky, instead of close dome-like clumps.
4. Any changed shore or mountain foot intersecting the depth-texture domain requires rebaking depth from the new actual saved triangles and rechecking scatter/collision support. Keep the four current island roots closed and connected to the lake bed.

The inherited350m camera-path failures, full1344 two-pixel gate failure, unknown future streaming/dynamic straddle coverage, hardware-GPU gap and complete GOAL acceptance remain open. This proposal does not authorize treating supplementary poses as original-reference acceptance.
