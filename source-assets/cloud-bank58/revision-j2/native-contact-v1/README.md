# J2 native-contact-v1: source-only native verification supplement

This supplement closes the known native-pipeline preparation gap without editing
any previously frozen J2 file. The original candidate, original union/math
checker, original preparation results/freezes, all J failure evidence and every
camera/material/light input remain unchanged. **No engine has run.**

## Use this entry for the later native trial

From the repository root, only after the parent schedules the native window:

`python source-assets/cloud-bank58/revision-j2/native-contact-v1/run_patch_contact58j2.py --run-approved-patch-trial`

The old `run_patch58j2.py` is retained as original evidence; it does not supply
this additional guard and is not the supplemented trial entry.

The new runner retains the same one-build / one-fresh-verify / two-fresh-render
sequence and 30 seconds / CPU2 / 1.5 GiB / 200,000-byte source bounds. It executes
`source_contact58j2.py`, which loads the frozen original source module:

1. Build uses its unchanged `build` function
2. Fresh verify first runs the original `fresh(..., 'verify')`. After that exact
   saved-source open and original checks, it reads V/F from the actual loaded
   `bpy.data.objects[bank]` through the original `geometry_arrays`; no mathematical
   rebuild, candidate arrays or predicted float32 arrays are substituted
3. The unchanged supplemental `check_coplanar_contacts58j2.py` then checks those
   actual readback arrays at **1e-8 m**. Non-indexed contacts, mismatched original
   AABB/coplanar pair counts, wrong source/array/code identities, original verify
   failure or any exception make the verification child fail
4. Every render process requires the completed successful contact proof and
   original verify report, their exact source/array/code identities, and a PID
   different from the fresh verification process, before calling original
   `fresh(..., 'render')`

## Evidence and fail-closed runner

`outputs/saved-source-contact58j2.json` is written before fresh verify, starts
with `passed=false`, and retains completion/error/actual checker output on
failure. On success it binds the actual native-array fingerprint, exact source
SHA before/after, same fresh verify PID, original verification-report SHA, and
supplement code SHAs. The original verify report is preserved separately and is
never relabeled to conceal a later supplemental failure.

The runner loads a new supplement freeze that includes every original prepared
input, every original terminal-frozen J2 file, both original freeze files, and
all supplement scripts/results. It copies supplemental source bytes, including
the unchanged contact checker, into `inputs/supplement-source-snapshots` and
places those snapshots in the before/after input identity checks.

After verify it requires the contact proof itself, hashes both proof and
original verify report, and copies them to `inputs/verified-snapshot-*`.
Original results and snapshots are checked before and after every remaining
stage and at terminal completion. The complete run's terminal freeze includes
these source/result snapshots and original outputs. A failed/nonzero verify
never reaches render; even a child exit 0 cannot bypass a missing/failed proof.
No source or evidence may be overwritten or rerun in place.

## Static verification, not native acceptance

Normal and optimized Python each pass **36/36** protocol/structural checks.
The executed fixture uses a clearly named fake source/core and no Blender. It
checks actual-array extraction protocol, immutable evidence, original failure,
checker failure, forbidden render without proof, source/PID/code/array/report
identity errors, coverage mismatches and tolerance changes. AST/source checks
confirm the dedicated freeze/entry, source and result snapshots, stage/final
immutability, failure-before-render branch and unchanged resource caps.

These tests do not prove a real Blender source, native contact pass, successful
render or visual quality. Those remain pending the one scheduled native trial.
`preparation-freeze-native-contact58j2.json` is the new source-only input freeze;
all original preparation records remain separately frozen and unchanged.
