# Separate finite 900-second observation, source preparation only

The sixth actual run remains a failed strict600 experiment: `cloud-evidence/nearbay61-orbit-renderer-20261002T070230Z-qx75unzy`, first exceeded `audit_begin`600.128s, child1 after612.132s, three captures and3.54159236/4rad. Its complete source snapshot, raw/gzip report, logs and results are unchanged. A future successful900 observation cannot repair this historical result or claim600 performance.

## Why a separate observation

600s was the harness's finite observation/performance ceiling, not the user's visual/path requirement. The recorded remaining0.4584076405rad needs ten more <=.05rad native inputs, event72 completion, final settling/capture/audits and final evidence. Read-only [timing analysis](timing/ANALYSIS.md) distinguishes overlapping measured timers from unmeasured wall: inventory61.868s includes nested15.904s hashing; the589.804s process-wall versus21.033s engine-delta difference is not assigned entirely to rendering. Conditional historical-cadence scenarios finish near694–713s.900 is plausible, not guaranteed: PI settling already used14.785784s of its unchanged15s local ceiling.

## Explicit modes and acceptance

- Default invocation remains native600 / outer720. The native entry now requires the wrapper's explicit `--observation-budget-seconds=600` argument, so missing/duplicate/unsupported native arguments fail instead of defaulting silently
- Only `--run-renderer --observation-budget 900 --wall-timeout 1020` opts into the separate900 observation.900 with an omitted720 outer default, a different outer cap, or parse/static mode is rejected
- The existing600 branch still permits a shorter explicit positive finite outer timeout, up to720, just as before. The fixture stays59; default parse/renderer outer cap stays720. No light fixture or parse receives a longer default
- Production accepts only the named600 or900 native budgets. The expected requested integer must agree with native report, completion receipt and terminal record, and their actual wall limits. Missing/wrong/unsafe budgets fail closed
- Every deadline boundary still reads actual `Time.get_ticks_msec()` from the first statement in `run()`. Completion includes source verification, full-report write/hash, receipt flush/rename/hash and final pre-cleanup clock; first timeout is sticky. No injected clock or unbounded extension
- `strict_600_performance_passed` is a separate explicit boolean in receipt/terminal/wrapper. Wrapper independently checks it against actual completion wall<=600 and overall success. A900 observation that completes at600.001–900.000 can have observation success but must have strict600=false. The large report names the terminal authority because it predates completion-clock observations
- Exactly900000ms is within the requested900 budget;900001ms fails. Default600000 remains within600;600001 fails in default mode. Wrong hashes, missing/duplicate/invalid records, earlier timeout, logged error, nonzero/missing child exit, cancellation or any input/dependency/absence mismatch still fails

## Narrow shared-helper change

`continuous-v6/wrapper_support.py` is changed and is **not** byte-identical to run6. Its new keyword-only `wall_timeout_limit` defaults720 and admits only explicit720 or1020. Without1020 opt-in, a timeout above720 is rejected. Main wrapper passes1020 only after validated900 renderer admission. The selected cap is recorded. CPU2 selection, process ownership, signals, hard kill/reap loop, logging and actual exit handling are unchanged; no grace period is added. Python-only tests launch and reap a short Python child under the1020 cap; they never wait1020s or invoke Godot.

Other production changes are `run_orbit61.py` (admission/evidence binding/result) and `verify_orbit61.gd` (budget parsing/deadline limit/report fields). Source-only test plumbing changes are `continuous-v6/test_wrappers.py` and `check_static.py`. The old deadline-v1 files and old wrapper-result files remain historical, unchanged; current test results live here.

No changes to world/native assets, resolution1180x664 (recorded capture1179x664), render method/settings, original4rad goals, .05rad step, .00001rad input tolerance, two-sample.02m settle,15/15/20s local event/settle/capture guards, near-plane envelope, all physical layers/LOS/visible sweeps, source/identity checks or ship0. Five mechanical helpers are byte-identical. All mechanical functions and the entire run sequence except initial budget admission are text-identical. No geometry, frame or input optimization is included.

## Validation and limitations

Current normal and `python -O` suites:29 existing wrapper groups plus19 deadline/budget/preservation groups. Budget tests include exact600/900 boundaries, explicit native admission, all3 records, true/false600 declarations, malformed/unsafe/missing values, wrong receipts, and hard source/child/log failures. Static/dependency validation checks the immutable1483 saved closure plus original1477 manifest. Tests use source-predicate translation and clearly synthetic JSON/stdout; no native clock or GDScript execution was tested. First launcher-test attempt accidentally called its mock; the failed assertion led to testing a freshly loaded real wrapper instead. No engine was launched during that correction.

Preparation is **not** a native parse or world pass. A future actual parse and new independent renderer run are required. Native visual/manual review, universal live-resource freeze, nearshore pixel coverage, flight, hardware-GPU and all-reference acceptance remain false. Preserve any new failure; do not add time, reduce resolution or weaken checks inside a running observation.

## Exact future commands (not executed here)

Working directory: `/workspace/scratch/a29d03198654/Aether`. Use the parent-coordinated actual graphical window, with no concurrent heavy job.

First parse only, retaining a short explicit60-second outer limit per script:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/coast61-nearbay-orbit/run_orbit61.py --parse-only --wall-timeout 60

Then, only after source freeze, publication/review and successful parsing, the separate long observation:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/coast61-nearbay-orbit/run_orbit61.py --run-renderer --observation-budget 900 --wall-timeout 1020

Default strict600 replay remains:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/coast61-nearbay-orbit/run_orbit61.py --run-renderer

Each actual invocation creates a new evidence directory and snapshots its own exact inputs. No old run is resumed or overwritten. Require real terminal native exit/log/source afterchecks and matching budget evidence before accepting the new observation. Even if completed under900, retain and report both this new observation result and the historical failed600 run.
