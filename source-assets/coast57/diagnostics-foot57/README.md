# Actual native feet on rejected57 Draft A

Read `actual-foot-support57.json` for all41 placements and `prop-foot-geometry.json` for the actual MultiMesh.mesh geometry. The target-only export read mesh arrays through SceneState, without instantiating the world or reading a headless MultiMesh buffer. `logs/feet-export-report.json` records exit0,7.01s and384640KiB peak RSS.

Pines use their actual six minimum-Y trunk ring vertices, edge midpoints and center. Rocks use actual surface triangles below the model's original root planeY=0, including true edge crossings and clipped-face samples. Each sample is transformed by the exact original/candidate buffer and compared with the corresponding original/candidate native indexed terrain. Positive delta means air under the sampled foot surface; negative means terrain penetration. The source/candidate are unchanged.

Seven placements worsen by more than0.1m of sampled air gap (2 rocks,5 pines), and6 worsen by more than0.1m of penetration. Worst gaps are4.560m and1.469m for rocks7 and6, and0.436m for pine poplar4. Rock burial can be intentional, so original measurements remain beside candidate values.0.1/0.25m are reporting thresholds, not new acceptance tolerances. Sampling identifies actual failed locations; it is not a continuous-contact or stability proof.

`logs/*-executed.*` preserve scripts exactly as executed before moving this diagnosis into its independent directory. The top-level diagnostic scripts now resolve the frozen parent source and write only here. No scene integration or new geometry/material edit was made.
