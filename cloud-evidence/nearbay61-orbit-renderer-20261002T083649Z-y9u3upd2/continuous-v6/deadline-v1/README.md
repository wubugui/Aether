# Strict total-wall acceptance correction, preparation only

The corrected X11/GL fixture at `cloud-evidence/nearbay61-continuous-v6-20261002T061937Z-zjkx_tqa` really passed61/61 with child/wrapper0, and the four corrected parses at `nearbay61-orbit-parse-20261002T061856Z-p7b7_x2x` passed. Their original source snapshots, reports and logs remain unchanged. They do **not** parse or execute the new deadline correction. No new engine or world run has occurred for this correction.

## Concrete gap closed

Previously600s was checked only at the beginning of active late-process sampling. A last sample before600 could be followed by expensive physics audit, capture, final source hashing or report writing after600, with no fresh check before `passed=true`. The720s process bound would not independently reject that600–720s interval.

`verify_orbit61.gd` now has one `within_wall_deadline` helper. It always reads the actual `Time.get_ticks_msec()`; callers supply only a boundary name and whether this is a completion observation. No synthetic clock or elapsed time can be passed into production. The first exceeded boundary/elapsed value is sticky. Finishing can fail without the ordinary abort callback recursively scheduling another finish.

Checks cover initial source hashes, scene startup and fixture boundaries, inventory/preflight, each actual process identity and physics audit, native event/settle waits, image write/hash/rays, capture completion, final identity and source hashes, report completion and receipt completion. Existing exact frame/input/clearance/ship/geometry checks remain. A timeout during finalization cannot be replaced by success later.

## Exact600/720 definition

The existing start remains the first statement in `run()`: `start_wall=Time.get_ticks_msec()`. Thus600 includes initial source hashing, saved scene load/instantiation, fixture deletion/process synchronization, inventory and preflight, all orbit inputs/process/physics/settling/captures, final identity/source verification, final large report write/hash, and completion receipt flush/rename/hash. A native final clock observation immediately before terminal metadata emission/cleanup is the acceptance point. The original comparison is preserved: elapsed milliseconds must be nonnegative and at most600000.

The terminal metadata merely records that observation. Subsequent native cleanup retains its original three frames/post-draw, queued game disposal, visual-query resource closure and eight frames. Cleanup and the actual native exit/logs remain covered by the unchanged720s child limit. This does not make600 a preemptive native-thread timer: a synchronous expensive operation is rejected at its next explicit boundary; the independent wrapper still kills/reaps at720.

## Small, independently bound completion evidence

1. Final hashes finish, and the helper checks total wall before the existing acceptance gates assign `passed`
2. The full `orbit-report.json` is atomically written and SHA256-read back; its completion clock is stored in `orbit-completion.json`
3. The receipt is flushed, closed, renamed and SHA256-read back; the helper checks the actual native clock after those operations
4. A final native check immediately before cleanup is emitted as one `ORBIT61_TERMINAL_WALL ` JSON line in preserved raw stdout, binding both file hashes and the actual completion wall. It does not falsely label the receipt's pre-write clock as post-flush
5. The wrapper requires strict JSON, one exact terminal line, both versions/true booleans/hashes, finite nonnegative wall values<=600, no prior exceeded boundary, precise boundary labels, consistent millisecond/second values and monotonic report→receipt→final ordering. Missing evidence fails closed. Actual child exit0, no timeout/cancellation/log errors and all original source/dependency afterchecks are still required

If final report or receipt work crosses600, there is at most one failed report/receipt rewrite, no recursive retry. An even later final check can still invalidate the terminal result and child exit; the wrapper never upgrades a provisional large-report flag by itself. Write errors remain logged errors and cannot grant a pass.

## Python-only preparation

`test_deadline.py` has10 groups: it evaluates the exact extracted source predicate in a clearly synthetic Python model, checks source ordering, and runs isolated wrapper acceptance/negative tests. Late audit/capture/final-hash/report/receipt after an earlier valid process sample is rejected. Missing/changed receipts/reports, malformed/duplicate terminal evidence, wrong hashes, negative/nonfinite/nonnumeric/>600 times, wrong/stale boundary, previous timeout and child failure are rejected. These tests never execute GDScript or a native clock.

The existing29-case Python wrapper suite remains29, with its positive mock payload extended to include explicit synthetic completion evidence. The shared launcher and its720s/signal/kill/reap behavior are unchanged. Current logs/results are retained in this directory and the existing current wrapper test files. Old native evidence remains tied to its old exact sources.

Modified production files: `verify_orbit61.gd`, `run_orbit61.py`. Preparation-only changes: `continuous-v6/test_wrappers.py`, `check_static.py`, current `WRAPPER_TESTS.json/.log`, and this independent `deadline-v1/` directory. No native scene, mesh, material, source asset, geometry/sequence/mouse helper or shared launcher is changed. Parent publication and then fresh native parsing/light validation are required before a new world attempt.
