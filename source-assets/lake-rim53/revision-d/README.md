# West rim53d: camera-informed native-source revision

Status: source prepared, graphical review pending, not integrated. Existing first/b/c sources and evidence were not overwritten. SavedGame51b and the project default remain unchanged. No GUI or Cycles process was launched for this revision.

## Observation and design decision

Both actual53b original-camera screenshots and both original reference images were inspected. Runtime source: `cloud-evidence/rim53b-world-diagnostic-20261001T052441Z-zv0suI/images/diagnostic-report.json`.

The highest world-space point was not the highest point in the image. The53b300m northern crest projected into1128 at11.15%width/35.35%height, while a closer276m shoulder atX259/Z-1783 projected to0.16%width/30.90%height and dominated the clipped silhouette. This explains why merely retaining a300m summit did not create a visible left peak.

53d moves the dominant nearer crest north toX245/Z-1880 and authors a323.5m rock crest,324.74m actual snow top. It predicts4.99%width/29.57%height in1128, close to the visually identified reference left apex. The northern crest becomes a lower283m shoulder. These positions/heights are authoring decisions derived from the recorded camera projection, not metric facts extracted from the artwork.

1129 remains a separate gap: the same new crest predicts18.04%width/34.45%height, farther right/lower than the reference left apex. The same peak identity has not been established across the artwork, and this revision does not claim both compositions match. `projection-analysis.json` records the actual camera transforms, source SHA, projection derivation, approximate reference anchors, and vertex projections for b/c/d. The next real diagnostic also records the actual main camera projection and engine`unproject_position` results directly.

## Native geometry

Five editable closed mesh objects,1,780triangles, zero boundary/nonmanifold edges and zero degenerate faces. The original340-triangle rock root remains unchanged after source-to-saved authority mapping. New geometry retains53c's constrained irregular geological control points, actual descending eroded channels, separate thick closed snow cap/gullies, and adaptive buried skirt. It does not use repeated longitudinal snow bands or scale the original cone.

`sculpt-report.json` contains component bounds, volumes, triangle counts and source authority. `native-readback-impact.json` independently reopens the saved`.blend` and matches all five component triangle sets to the payload at0.1mm precision. Material intent remains the existing verified51b mountain ShaderMaterial with vertex palettes; no new engine shader/material conversion is part of this source.

## Protection and impact

- Actual18building footprints and the northern50m buffers:2m support probes differ by at most0.000366m numerical tolerance
- Entire new component footprint:277,565m², continuously contained within the union of actual savedY≥0terrain/mountain triangle projections; zero area enters an old water column
- Root edges:4,210independent0.5m samples, all below actual saved support with at least approximately4m burial margin
- All1,261neighboring scatter indices checked:1,141unchanged;120have changed support, all inGround_0_-3. Every affected index and support delta is recorded. No relocation transforms have been applied or proposed yet for this revision
- Existing native terrain geometry, villages, underwater carve, islands, cameras and saved collision resources are untouched

The initial package's209scatter edits are obsolete for this geometry and must not be reused. A source visual pass must be followed by fresh scatter reconciliation and a full native integration/reload, collision and depth-source verification. This package is not a saved gameplay candidate.

## Graphical entries for parent scheduling

- `launch_world53d.sh`: two actual-world screenshots at original1128/1129; temporary visual replacement of west only, prominent UNINTEGRATED banner, original collision and scatter deliberately retained. Includes input hashes, unique run directory, terminal exit code, actual image sizes, material and reflection state, and saved51b/scatter/collision preservation checks
- `launch_preview53d.sh`: isolated five-view same-light source inspection

The world script passes headless syntax/parse validation and then refuses rendering with intentional exit2. Both wrappers use external tools-feiting runtime directories, Dummy audio and disabled VSync. Actual screenshots have not yet been produced for53d. Numerical checks and projection predictions are not a visual pass.
