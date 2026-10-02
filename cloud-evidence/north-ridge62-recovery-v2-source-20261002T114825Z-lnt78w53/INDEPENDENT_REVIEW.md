# Independent review of the actual saved north-ridge62 source

Reviewed 2026-10-02 after the completed source run. This review read the original saved raw pair, source bytes, native/process reports, flushed event streams and protection manifests. It launched no engine, rewrote no source/raw evidence and produced no image. A separate geometry check independently reconstructed the actual arrays/projections without using the contract validator; the existing full validator was also replayed against both actual raw files.

## Result

**Actual source build and independent fresh-open evidence passed.** This is an editable source/identity result, not a visual, support, world-integration or weather result. No views have run. All167 support cases, source-form review, world integration and completeGOAL remain open.

- Saved source: `source-assets/north-ridge62-authoring/recovery-v2/north-ridge62.blend`, **10,004,835 bytes**, SHA256 `dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502`
- Wrapper exit0, **15.644937366s** against120s total
- Build PID5 exit0,3.329257732s against75s; independent verify PID24 exit0,2.623352256s against30s
- Actual CPU affinity[0,1] throughout; no timeout/RSS stop, logged engine error or leak
- Peak observed wrapper+childRSS582260KiB; conservative largest child peak plus wrapper peak719468KiB, both below1572864KiB

## Raw and process chain

`build-raw.json` is14,837,932 bytes, SHA `c941a75a43a5c4f88d4083c403cb9f3219752c49056405bed66840803b0f629b`; `verify-raw.json` is14,837,933 bytes, SHA `9e476591b52fe1980bc9a55019914c6a555fa75dc97ad4e70bedb5194d037633`. Every raw field is equal exceptPID; affinity is also equal. Native report PID, process report PID, wait4 exit and raw SHA agree. Actual terminal validation exactly equals an independent replay of the frozen validator on each saved raw.

Build66 and verify24 native events match their JSONL, stdout `NORTH62_STAGE` lines and terminal event arrays exactly. All eventPIDs agree with their child; wall/user/system CPU and peakRSS values are monotonic. Native last-event counters are build wall2.728444773s/user2.755838s/system0.296162s and verify wall2.194658236s/user2.268284s/system0.228294s. These Python-stage counters differ legitimately from full wrapper child wall.

Observed spans: compact binding internal load0.026032592s; rebuild0.338702060s; build capture0.214693919s; fresh open0.010405583s; verify capture0.211737143s. Both full validations take about0.902s. This demonstrates the new implementation fits its bounded attempt; it does **not** identify the old uninstrumented timeout's exact executing line or retroactively pass that failed run.

## Actual geometry, editing data and materials

Five actual mesh vertex counts are4326/6144/6144/6058/6009; face counts8192/2048/2048/2048/2048. Every position float32, face/index order, original source-localXYZ andRGBA value matches the original mappings and frozen proposal. Nonzero group memberships3659/9732/2086/7106/1983 total24566, with all native weight bits exact. All eleven attribute schemas/values, source triangle/tile/corner mappings and loop topology pass.

The1246 per-tile overrides map to1229 changed master points and2479 changed master faces. The other3097 master points and allXZ remain original. The highest point is uniquely main vertex826 at Godot world(-2460.00244140625,745,-4830.61279296875). Master positions SHA remains `30b541d723bccaef3d5b7bae5f1569bfe65c9c67b256a451ddf33deb382f4a40`; faces SHA `b8e3c68f61e62ebc2b82ab8346a33aed6ed1336cd1ad0a53f6f6dc8de3536783`; candidate worldY SHA `2eca5d39aedc03678f7d4611aa8aa497bb616ec9e7b5bade5da16db5284d13d5`.

All27 controls,40 control faces,15 height-only handles, object transforms and three editable material definitions match. Master grass/rock/snow face counts are5534/2589/69; roughness and base colors equal their intended native float32 values, metallic0. This is a neutral editable material study, not world material/weather acceptance.

All five meshes are flat, nondegenerate and upward-facing. Polygon-normal maximum geometric error is2.8813858899e-7; actual corner-normal maximum is2.3827965279e-5, both below the unchanged3e-5 gate. Each face's three corner normals are bit-equal; polygon and corner normals are correctly not required to be mutually bit-identical. Minimum triangle double-area is57.6329686184; minimum upward normal component0.1486537516. The steep-face visual risk remains.

All five embedded Texts have exact expected bytes/hashes, are in-memory and have empty filepath. The binding's intended no-finalLF compact bytes survive; code/readme terminalLFs survive. Fresh reopen retains the self-contained BULK helper and complete original editor data. No external library/image dependencies are present.

## Fixed cameras and protection

Original1131/1347 eye positions are exact. Their actual matrices differ from independently reconstructed target orientations by at most1.3866023169e-7/1.6702618871e-7; verticalFOV error is−1.3023913725e-8 radians relative to55°. No retarget occurred. At1179×664 the actual main peak projects approximately to(905.0639,93.7696) and(961.9724,102.2876) pixels. All15 semantic-point projections stay within0.000129px of the frozen preparation. Side/back matrices and all render settings also match. These are geometric projections, not rendered visibility or cloud-occlusion proof.

All**115 frozen input files plus the freeze manifest itself** match the actual recorded input dictionary and were independently rehashed unchanged. The7364-entry before/after original-protection dictionaries match exactly; their identical file SHA is `98e4ea3ad262e0a643968200ea150af9da3340fcdcaa40f89d0ea52383d352a0`.

A later current-filesystem rehash found7363 of those7364 paths still identical. The sole later difference is the separately developed `source-assets/cloud-bank58/revision-k/world-trial-v2/relocate58k.py`: actual run before/after both recorded `a8c5d2c22e83858ec8d74d9ff3077a44e04a842f4dd7519fef707d3616f17deb`, while this later read saw `e905591d758506909b723724727237be7db04a4689e788a1f226cb6c46bfb679`. This later edit does not alter the completed run's identical before/after evidence; no blanket claim that the whole current workspace remains frozen is made.

No saved-world/default entry, protected coast/lake/cliff, scatter placement or existing source was changed by this source attempt. The original60s timeout remains failed and retained. External storage/chunk restoration and a clean restored-source fresh-open are separate pending checks, not covered by this local source result.
