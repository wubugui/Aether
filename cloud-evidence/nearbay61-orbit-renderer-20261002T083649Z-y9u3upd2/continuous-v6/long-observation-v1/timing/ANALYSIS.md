# Historical orbit timing and separate long-observation plausibility

Source: `cloud-evidence/nearbay61-orbit-renderer-20261002T070230Z-qx75unzy`. Read-only analysis of the original report, logs, sequence, events, telemetry and frozen source snapshots. No engine was invoked. Source hashes and the verified gzip/raw round-trip are in `historical-timing-analysis.json`.

## Result that must remain unchanged

The strict 600 native run failed at `audit_begin`, 600.128 s. The terminal clock is 601.325 s; child exit was 1 after 612.132 s. The 720 s outer limit did not trigger. `wrapper_exception`, `passed=false` and `first_item_runtime_passed=false` remain failures. Native `complete=true` means the final report was written, not that the path passed. A future 900 s observation is separate evidence and cannot repair the 600 s performance result.

## Measured work, with scope

- Preparation 40.151818 s, including initial source hashes 1.006613 s and scene load/instantiate 6.345950 s; preparation also includes fixture/draw/process waits and other work
- Initial inventory preparation 0.551496 s; 1385 inventory validations 61.868020 s (44.670 ms mean, 113.485 ms max). Counts reconcile as 154 active-process validations + 1230 physics callbacks + 1 before-F2 validation. Many physics callbacks have no new pending camera segment
- 1,120,612 MultiMesh hashes over 4,015,796,928 bytes: 15.903756 s. This timer includes byte conversion/hash work and is nested inside other phases; buffer retrieval precedes that timer
- 233 physical sweeps 0.006137 s; 233 isolated-visible sweeps 0.002471 s; 306 native line-of-sight rays 0.005281 s. The 80-segment desired-arc preflight was 0.001543 s and includes some of those sweeps
- Three image extractions/saves 0.264656 s total, plus local capture rays 0.000771 s. These are not total capture latency: draw and own-frame audit waits are elsewhere
- Final 1568 source hashes 1.009732 s. Final report snapshot contains six completed report writes 0.229758 s and one open write; later cleanup progress records seven completed writes 0.287052 s

These timers overlap. They cannot be summed and subtracted from total wall to identify rendering cost. No per-frame rasterization, scheduler/off-CPU or driver wait profiler exists in this evidence. llvmpipe is recorded, but causation and the remaining wall-time partition are unmeasured.

## Wall versus engine time

Final-report telemetry records 589.803796 s of process interarrival wall and 21.033333 s of accumulated engine process delta: 568.770463 s difference, 28.0414× ratio. This is a clock/cadence discrepancy, not a measured rendering bucket. Telemetry covers 158 callbacks; 154 active camera samples span 556.140879 s with 20.532308 s summed sample deltas. Successive active samples advance exactly 8 physics frames in this trace. Source confirms physics inventory validation is performed each callback, even without a pending segment.

Clock scopes differ: watchdog begins at run entry, telemetry at object construction, sample timestamps use engine monotonic epoch, wrapper wall spans child lifetime. The exact run-entry tick was not persisted. Therefore milestone ticks below are not falsely presented as exact watchdog-relative times. Final progress includes cleanup and must not replace final-report acceptance.

## Milestones and remaining path

Capture milestones (sample engine-epoch seconds; exact matching physics witness seconds):
- Default, frame 6: 43.812333; 44.657755
- 2.6 rad shore, frame 115: 437.196126; 441.481036
- PI ship-side, frame 142: 543.981485; 547.430144

All three captures' own sampled segments were audited. At failure: 72 delivered motions, 71 completed event protocols, 154 samples, 153 audited segments. The last observed angle is 3.5415923595 rad (88.54% of 4 rad), with frame 157 pending and active event 72 still requiring a strictly newer audited process sample. The 233.056807 m camera path is observed; ship path is 0 m. Every recorded audited segment is clear; that does not certify the missing segment or the unfinished path. The 80 preflight segments test the intended arc only.

Remaining angle is 0.4584076405 rad: ten additional <=0.05 rad inputs (nine full steps, then about 0.008408 rad under float32 accumulation), not nine. Finish event 72 first, then those inputs, final settle, fourth image and its own-frame audit, input release, identity/source checks and terminal receipt. The first 2.6 rad target needed a tiny corrective 53rd input, so the modeled whole run has 82 actual inputs rather than the 80 preflight chords.

## Separate 900 s native / 1020 s outer observation

Recent cadence supports a bounded experiment, not a guarantee. After PI, 14 sample intervals averaged 3.569541 s (3.365545–3.781532 s); shore-to-PI motion averaged 4.000456 s. Assuming roughly 26–28 interval equivalents remaining plus 1.1 s final bookkeeping gives about 94–101 s extra at the late cadence, or 105–113 s at the shore-to-PI cadence. Anchored conservatively at the 600.128 s failure boundary, those planning scenarios finish around 694–701 s or 705–713 s. The full observed sample-gap maximum was 6.160837 s, so one mean is not an upper bound.

A separate 900 s ceiling is plausibly sufficient without reducing resolution, input/physics audits, capture goals or source checks. It leaves meaningful margin over those conditional scenarios; 1020 s retains 120 s outer cleanup/safety headroom. It does not guarantee the unchanged local guards: event 15 s, settle 15 s, capture 20 s. The PI settle itself consumed 14.785784 s from completed-event audit to second stable sample audit, already close to 15 s. New angle-dependent costs or scheduling could fail a local guard even with global time remaining.

Keep any new observation's outcome and budget explicit. Regardless of that outcome, the historical 600 s failure stays failed. No reference-visual, nearshore pixel coverage, flight, hardware-GPU or universal live-resource-freeze acceptance follows from this analysis.
