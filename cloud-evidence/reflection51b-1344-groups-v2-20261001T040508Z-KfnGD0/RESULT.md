# Isolated1344 control result

This run exited0 with seven rendered PNGs. An independent Pillow RGBA8 decode confirmed that all seven images are byte-identical: SHA256 `f2de37ae3161bf1a537f4a3a6ad3709e7d1e0cc0a02d4dc5398cbc178d64fcf7`. This includes the same-value original-material copy baseline, Ocean-only conversion, native-only conversion, custom-only conversion, full conversion, and two restored copy-baseline views. See `images/independent-isolated-controls.json` and the engine's `images/group-report.json`.

The earlier complete seven-reference run remains a recorded failure: `../reflection51b-verify-full-20261001T032554Z-975juK/images/report.json`. At1344 its copy-baseline versus converted comparison differed at(870,340) and(870,341), with maximum channel difference2. Original restoration was exact; the six earlier reference controls passed. That report and its40images are unchanged.

The two-pixel failure did not reproduce in this isolated-reference run. No cause, repair or tolerance-based acceptance is claimed. Because every family comparison was zero, the adaptive same-RID official/plain-versus-guard branch was not executed; this run does not establish that the official template itself caused the earlier difference.

The original conversion gate stays false. Subsequent shared-world reflection/movement testing is an independent limited check and cannot override it, the inherited350m motion failures, or the remaining visual/reference-composition work. Saved51b SHA remains `b169f62527a52b9f2a3f091c2d7db136ad7cd67111e405f08f390eeb082e2bb1`.
