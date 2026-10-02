# Independent review: fixed K work-copy relocation and renderer v2

Reviewed 2026-10-02 12:04 UTC. **Source preparation accepted for the parent's separately scheduled one-time relocation, read-only shared-namespace check, and bounded renderer.** This is not evidence that any actual relocation, GUI namespace readback, Godot execution, image capture, or visual acceptance has succeeded.

The reviewer read GOAL and the current CLOUD_RESUME entry, the v1 wrapper and terminal evidence, and all v2 source. The only repository file written by the reviewer is this report. No real work-copy member was moved or rewritten; no engine, GUI query, Git operation, or CLOUD/GOAL edit was performed.

## Fixed authority and unchanged experiment

- Independently verified the original 47-file freeze `4c99da76ec61bae16a3ec445f187286ef68471d1261bef989eb1c2bb352ae148`, successful parse terminal/report, and complete parse manifest `0cc6c72f733f51320a460a1e31be153b1516aafba3576abe792a3569685201ea`.
- Independently hashed the actual original `/tmp/cloud58k-world-trial-v1-d92irkqc`: all **4889 files** match the original parse manifest; its **93 directories** are recorded. The fixed destination `/workspace/scratch/a29d03198654/Aether-working/cloud58k-world-trial-v2` does not yet exist. Source device 39 and shared workspace device 27 differ, so this is explicitly a cross-device per-file move rather than a same-filesystem rename.
- The original main project's **4884 files** still equal the accepted protection manifest. The old failed renderer report and terminal remain unchanged, correctly recording zero native process and zero images. The inaccessible GUI `/tmp` path is not treated as proof that the original copy disappeared.
- The v2 renderer requires a successful same-v2-freeze relocation receipt, exact original parse authority, SHA-bound before/after relative tree manifests and root/directory identity records, source absence, and a full hash of the actual fixed destination. It performs no second project copy, parse fallback, import, or reconstruction.
- Independently compared Python ASTs: after removing only four local alias bindings, the entire v2 `validate_images` body exactly equals the original successful v1 renderer image-validation branch. All four ordered PNGs, packed geometry/material identities, original/K front camera and projection equality, 1216/.35 weather, PNG SHA/IHDR/native Image **1179x664**, and restored opt-out gates remain intact.
- The actual trial GDScript, native scene and observation template are unchanged. Original anchor, one-root replacement, material, geometry, weather, cameras and known visibility/gap risks remain unchanged. The original **240-second native / 300-second wrapper / CPU2 / aggregate 3 GiB** renderer limits and process supervisor are reused. There is no new display discovery, display server, network, or permission operation.

## Migration safety and resolved findings

The move exclusively creates each destination file, streams at most 1 MiB at a time, verifies source identity and streamed SHA, independently rehashes the destination, preserves metadata, and syncs the destination before removing its exact verified source. Source and destination signatures are journaled around removal. Newly created directory entries and the first journal entry's parent are synced. The final destination must have exactly the original relative files, hashes and directories before empty source directories are removed.

Any ordinary failure stops migration and retains the available files and journal. There is no automatic retry, resume, rollback, overwrite, tree rebuild, or fallback copy. The per-member partition reports source/destination hashes, recovery status and individual read errors. A failed one-shot remains blocked for separate review. These are source and synthetic-test findings, not a tested claim about real cross-mount or power-loss behavior; SIGKILL or unavailable storage cannot guarantee final JSON.

The producer resolved these review findings before this verdict:

1. Added separate SHA-bound before/after records of the root and every directory's device, inode, size, timestamps and mode, in addition to relative membership and content manifests
2. Made partition reads record errors per member and side, and separated partition, main-project and frozen-input final guards so one failed guard does not silently skip the others
3. Kept an explicit 180-second migration-phase limit and remaining 300-second outer timer through final protection work, with exhausted-deadline checks before each final guard
4. Synced the newly created evidence/work directories and first journal's directory entry before relying on durable file-level progress
5. Propagated `InterruptedError` before handling ordinary `OSError` in partition reads. An independent tiny fixture reproduced the earlier cancellation-swallowing bug; the final code and new negative control preserve cancellation

The journal and partition are saved diagnostic artifacts but are not separately SHA-bound into the success receipt. This does not block this bounded experiment: renderer admission relies on the bound complete before/after trees and directory records and independently rehashes the actual destination. A failed migration remains ineligible for rendering regardless of its diagnostic contents.

## Independent checks

- **16 pure/synthetic tests in normal Python:** passed, 0.554 s
- **16 pure/synthetic tests in optimized Python:** passed, 0.501 s
- **Read-only `check_preparation58k.py`:** passed, 5.061 s tool wall time; 26 frozen files, actual 4889-file/93-directory original copy intact, 4884-file main project intact, fixed target absent, no v2 actual attempt or terminal
- **Three independent full-wrapper microfixtures**, using only disposable `/tmp` trees with two tiny synthetic files and empty directories: normal completion; journal failure before the first unlink retaining one verified pair plus the unmoved member; partition failure still completing both main-project and frozen-input guards. Expected terminal outcomes were 0, 1 and 1; every case retained an unchanged synthetic main project and started no engine
- Independent source-level AST equality and read-only original manifest verification also passed before the final suite

No fixture used the actual bound work-copy paths or attempted real cross-device movement. No PNG, native asset, world geometry or graphical evidence was generated. Actual shared-namespace access and rendering must still succeed under the parent's existing schedule; visual suitability, hardware GPU and complete GOAL acceptance remain unproved.

## Reviewed identities

The pre-review 26-file freeze is `5210991907a8208b4a7455db9fb0890e18d24612b7290f414c81c8449075f609`. The producer must add this report to the final freeze and rerun preparation checks without changing reviewed code.

- `binding58k.py`: `d4e8eebfd6d99467edbdd0aad4190a442e22bc9e649a527101bdf89af2021588`
- `relocate58k.py`: `4525b837b4899fed6441f8331ec7ccfc5e67a82da497810446b646592e4d5183`
- `run_renderer58k.py`: `bd09f64baf730e8a32167c11bb14d3adceecd5a651a1720efc4962b16895ef64`
- `check_preparation58k.py`: `48e924b4bb9704a04476cbfa621184e027170554d37654552ff64d876b0e094b`
- `test_v2.py`: `e8a5023fb29adb309037731e00e9f629becef8ce0eb4b675b58da31371b0a6ca`
- `README.md`: `be637f207678e2ecdbf648150ea887c69b305f1e1f92a9efad7b3ee0dd8ef150`

