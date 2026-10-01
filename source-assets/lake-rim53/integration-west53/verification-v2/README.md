# Fresh verification v2 after independent full-baseline rays

The native west-only build succeeded in `cloud-evidence/rim53d-west-build-20261001T063353Z-eEO0XE`. Candidate SHA256: `6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18`. Do not rebuild or overwrite it to fix validation expectations.

The original verifier failed before images in `cloud-evidence/rim53d-west-verify-20261001T063446Z-SG7QYY`. Its original input and failed report remain unchanged. All1,261scatter cache entries, the120updated/1,141unchanged instances, native graph, original root mesh and material/ready checks passed. The actual scatter support error was at most0.000610m and position error0.00000573m. Its aggregate support gate failed because4northern building-buffer expected heights omittedGround_1_-4: the offline source intake contained only6neighbor tiles, but these northern rays need an additional tile.

## Independent proof

`probe_full_baseline.gd` loads the full actual saved51bscene into the real renderer/physics world and executes the exact original171building/buffer layer4rays, without the six-tile filter. It changes no saved resource or threshold and loads no candidate. Its completed result is:

`cloud-evidence/rim53d-full-baseline-probes-20261001T064320Z-3Zwd4U/full-baseline-building-probes.json`

All171rays completed, physics-freeze preserved modes/layers/RIDs, and baseline ray-versus-ground_height error was≤0.000366m. Compared with the already recorded candidate physics rows, all171differences are≤0.000488m. The4old expectation errors are indices5,8,37,38, all hittingGround_1_-4. Their old expectation errors were0.103149m,29.288696m,86.887817m and60.758179m. The actual baseline and candidate heights agree.

`baseline-proof-binding.json` fixes the successful report's exact path/SHA, baseline SHA and original ray-input SHA. This is validation provenance, not a modification of the original build manifest. The original141immutable build inputs are unchanged.

## Next process

Run `launch_verify_west53_v2.sh` by itself. It uses the fixed successful baseline report, checks its hash and completeness, verifies each original building region/index and exact engineVector3ray identity, and compares the actual candidate against the independent full-baseline heights. All171building checks remain; the3cmthreshold,42mountain checks,1,261scatter checks, strict native graph checks and original motion results remain unchanged. The old partial expected values and all4corrections remain in the v2report.

This is a separate process after the baseline probe, so no second live world is retained. The baseline PackedScene references and audit cache are dropped before candidate live rendering. Default output is10actual screenshots plus `verify-report-west53-v2.json`; optional`--front-only` remains explicitly a2image smoke run. No candidate/default/source resource is written by verification. Graphical/reference acceptance remains false pending image review.
