# Independent review: separate long observation

## Finding

No blocking implementation issue found in the reviewed source. The explicit long experiment preserves default 600/720 behavior, binds the selected 600 or 900 native budget in all three completion records, and keeps the strict-600 result separate. This is a read-only source review, not native execution or runtime acceptance.

Reviewed against immutable sixth-run snapshot `cloud-evidence/nearbay61-orbit-renderer-20261002T070230Z-qx75unzy`. No native executable, test suite, Git command, external app, or resume/configuration file was used or changed. Only this review file was written for this review. Python AST parsing passed for the three reviewed Python files; no GDScript parser or clock was exercised.

## Budget admission and clock

- Main defaults remain `--observation-budget 600` and `--wall-timeout 720`. The legacy ability to choose a shorter positive outer timeout at 600 remains; arbitrary extensions do not
- The only admitted native budgets are exact Python integers 600 and 900. Booleans, floating budgets, missing values and other integers are rejected. Outer time must be a finite non-Boolean number, positive and within native budget + 120
- A 900 observation requires exactly 1020 outer seconds. Both CLI and `execute()` reject 900 when `run_renderer` is false, before source admission/child dispatch. Thus static/parse modes cannot opt into the long experiment
- Shared launcher default cap remains 720. Its new keyword-only cap admits exact integers 720 or 1020, rejects nonfinite/unsafe timeouts, and records both selected cap and actual timeout. Main wrapper passes native budget + 120 only after its stricter validation. Process ownership, two-CPU affinity, signal handling, monotonic parent timeout, kill/reap, and exit-status handling are otherwise unchanged. A normalized AST comparison of the complete `run_child` function exactly matches the sixth snapshot after removing only the new keyword-only cap argument/result field and replacing the new admission checks with the old timeout check; no kill/reap/CPU2 body changes remain
- Native renderer receives exactly one explicit `--observation-budget-seconds=600` or `900` from the wrapper. Native admission independently counts arguments and accepts only literal strings `600` or `900`; missing, duplicate or malformed budget arguments exit 2 before output creation, hashing or world load
- Native deadline still computes `Time.get_ticks_msec() - start_wall`; `start_wall` is assigned once at run entry before source hashing and world loading. No elapsed-time parameter or injected/mock clock was added. The cap comparison remains inclusive at the exact endpoint and first-exceeded state remains sticky

## Completion-record agreement and strict-600 meaning

- The native report, receipt and terminal record must each have an exact integer `requested_observation_budget_seconds` equal to the wrapper's requested budget; each `wall_deadline.limit_seconds` must be a non-Boolean numeric value equal to it. Missing, wrong and unsafe values fail closed
- Receipt and terminal still require their specific versions, literal successful runtime flags, exact report SHA, expected completion boundary, finite nonnegative elapsed time within the selected native cap, empty first-exceeded state, exact millisecond/second agreement, and consistent last-check time
- Strict JSON parsing rejects duplicate keys and nonfinite numeric encodings. Exactly one terminal line is required. Its receipt SHA must match the completed receipt; terminal time cannot precede receipt time
- The report intentionally does not claim its own authoritative strict-600 result because its serialized clock precedes receipt and terminal completion. Its new authority text points to those later records. Native receipt/terminal `strict_600_performance_passed()` uses the actual completion clock and requires native success and elapsed <= 600
- Wrapper demands a literal Boolean strict-600 declaration consistent with each later record's time. Final wrapper strict-600 can only be true if the entire renderer result, child exit, logs, source checks and terminal strict-600 result pass. Completion after 600 under a 900 budget can pass the separate observation but cannot pass strict-600
- Crossing 600 between receipt and terminal correctly permits receipt true/terminal false, with wrapper false for strict-600. Crossing the selected global cap still invokes the existing failed rewrite and terminal failure path. No success can be restored after the sticky deadline failure
- Hashing, receipt flush/close/rename/hash, final real clock sample before terminal emission, cleanup, and actual child exit retain their original ordering. A missing receipt or terminal, failed exit, timeout, wrapper signal, logged error or source mismatch cannot be rescued by apparently positive timing data

The sixth run itself remains unchanged: strict 600 failure at 600.128 seconds, native exit 1, wrapper pass false. New schema checks do not reinterpret or overwrite it.

## Mechanical invariants compared directly

Five helper files are byte-identical: `visible_geometry61.gd`, `native_sequence61.gd`, `native_mouse61.gd`, `orbit_telemetry61.gd`, `fixture_lifecycle61.gd`.

25 existing GDScript function bodies are byte-identical, including all motion, input mapping/delivery, process sampling, pending-physics audits, actual image capture, settle/event wait, ray/sweep, geometry classification and fixture synchronization code. Only these existing bodies differ: `_initialize`, `finish`, `report`, `run`, `wall_deadline_snapshot`, `within_wall_deadline`, `write_completion_receipt`; the sole added function is `strict_600_performance_passed`.

The `run()` body is identical after removing its single early budget-admission line. Consequently the fixed fixture, 1180×664 requested window, four captures, 2.6/PI/4-radian goals, <= 0.05-radian steps, <= 0.02m two-sample settle, right-mouse native events, every actual sampled segment and its exact physics audit, zero ship movement, MultiMesh/identity observations, local timers, frozen-source checks and no-flight/no-scene-save behavior remain in place. Finish acceptance still requires all samples audited, four captures, released inputs and unchanged stationary ship, plus the selected global deadline. The live-resource and visual-acceptance limitations remain explicit.

## Test-source review

The suite covers endpoint/overrun logic for both native budgets, original strict-600 boundaries, malformed/missing budget declarations in all three evidence records with hashes rebound, strict-600 declaration inconsistencies, exit/timeout/signal/source/log/receipt failures, and unchanged mechanical bodies/helpers. It labels synthetic native records and translated predicates as source/Python-only, and makes no native-clock, GDScript parse, GL or world-success claim.

The launcher-test repair is present: it loads `actual_child_runner` afresh before invoking production `child_run`, rather than calling the mock installed by `prepare_orbit()`. This provides the intended real-Python-child path when the parent runs the suite. I did not execute it; parent test reports are separate evidence.

The test result now hashes `continuous-v6/wrapper_support.py`, resolving the earlier reproducibility recommendation.

Additional optional test hardening: mutate `wall_deadline.limit_seconds` independently in all three long-mode records, rebinding hashes, and exercise receipt strict-600 declaration corruption as well as terminal corruption. Current production checks cover these cases by inspection; the existing new tests focus their all-three-record mutation matrix on `requested_observation_budget_seconds`.

Historical performance risk remains: original PI settling used 14.785784 seconds of its unchanged 15-second local guard. A 900-second global budget cannot prevent a local settle/event/capture timeout. This is a measurement caveat, not a regression introduced by the source change.

## Reviewed identities and locations

These identities scope the review to the bytes read; later edits need rechecking.

- `run_orbit61.py`: `67af7d30ffdf28e2606cfb556a1bbd83e970a450188f4624a4610d5a053c4ed6`
- `verify_orbit61.gd`: `c899666724e0b828f374843281c13d4953e9f8ceeb69bd17e752b00bda927073`
- `continuous-v6/wrapper_support.py`: `cbb2708a26522c6137fe53fb6231b2779c8da6647727a998d28bf55c3e0a1aef`
- `continuous-v6/long-observation-v1/test_long_observation.py`: `3146a02372449e03f9cad9cb3c73307b2ff29aeed336a80010835de0f41e4757`

- `run_orbit61.py`: `def validate_budgets` at line 54, `def child_run` at line 173, `def validate_completion` at line 180, `if args.observation_budget == 900 and not args.run_renderer:` at line 259, `if (type(runtime.get` at line 314, `result['strict_600_performance_passed'] = bool` at line 347, `parser.add_argument('--observation-budget` at line 366
- `verify_orbit61.gd`: `func within_wall_deadline` at line 100, `func _initialize` at line 131, `func report` at line 150, `func finish` at line 431, `func strict_600_performance_passed` at line 474, `func write_completion_receipt` at line 477, `func run` at line 506
- `continuous-v6/wrapper_support.py`: `def run_child` at line 73, `if type(wall_timeout_limit)` at line 84, `'wall_timeout_seconds': timeout, 'wall_timeout_limit_seconds'` at line 93
- `continuous-v6/long-observation-v1/test_long_observation.py`: `def test_requested_budget_missing_wrong_or_unsafe_fails_in_all_three_records` at line 250, `def test_false_or_missing_performance_declarations_fail_closed` at line 277, `def test_mechanical_function_bodies_and_helpers_unchanged` at line 306, `real_runner=BASE.load` at line 335, `sources=[` at line 359
