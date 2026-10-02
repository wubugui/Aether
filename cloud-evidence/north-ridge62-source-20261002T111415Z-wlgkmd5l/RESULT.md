# North source first native attempt: rejected by its time budget

Actual run on 2026-10-02 11:14 UTC. This is a failed source creation attempt, not a completed editable source or visual result.

- Wrapper exit 1, total 55.138630250 seconds against the original 60-second total budget
- Only build child ran: PID 5, CPU affinity [0,1], actual 48.703885249 seconds, return -9. Its remaining allocation was 48.651942365 seconds; timeout_triggered=true. The inherited helper ceiling of 720 seconds was not this run's allocation
- Actual child peak 338460 KiB, sampled aggregate 390320 KiB; RSS limit was not triggered
- No completed .blend, raw readback or PNG was produced. Fresh verification and all four views never started. stdout/stderr are empty; the original run had no useful phase marker, so the exact stalled operation is not established
- All 77 frozen inputs and 7336 original protected files remained unchanged; earlier outputs remained unchanged
- saved_source_unchanged=false and source SHA/bytes null describe the absence of the requested new file, not a change to an original asset
- No Godot/world load, geometry integration or support placement. All 167 support rows remain unresolved for integration, and visual/GOAL acceptance remains false

## Preservation

Original wrapper, process, progress, logs and admission/terminal records are preserved unchanged. The two full 1440730-byte protection manifests are losslessly gzip-stored with raw and stored identities in storage.json. The snapshot retains the original 5424728-byte bindings identity, stored as the exact previously published XZ; see its STORAGE.md. Original raw files remain local and ignored. Runtime extension cache is excluded, not project evidence.

## Next isolated candidate

A separately named recovery may optimize equivalent bulk attribute access and loading the identical long embedded text, and add flushed phase/timing records. The original no-phase failure cannot prove a text-writing bottleneck. Any new finite budget is explicit and does not retroactively pass this original 60-second attempt. Geometry, controls, exact weights, embedded text bytes, material, protection and fresh-reopen gates remain unchanged. No automatic retry or view stage has run.
