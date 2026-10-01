# Bounded recovery after the interrupted52e observation

The actual original run is `../cloudsea52e-paired-20261001T050129Z-geTptG`. Baseline51b completed16 images and exit0. Candidate52e saved nine reference images, then exited137 while entering the first close-view sequence. The exit record timestamp is approximately05:10:50UTC; the cause is unknown. Neither OOM nor an engine crash is established by this exit code.

The nine PNGs decode successfully. `interrupted-nine-image-ledger.json` records their exact bytes, SHA256, decoded dimensions and literal corresponding save/physical-clear console PASS lines. It intentionally leaves camera/environment/cloud-center runtime fields null. The missing candidate `report.json` cannot be recovered from the script's intended behavior or the baseline report.

## Definite retained objects in the original verifier

The original `run()` retained local `base_packed`, `cand_packed` and `base_state` until its awaited observation loop returned. Freeing `other` disposed the other node instance but did not release those local PackedScene resource graphs or the large canonical-state dictionary. The cloud triangle arrays also stayed alive intentionally for geometry queries. These are identifiable retained objects, not proof that they caused SIGKILL.

The new observer loads one fixed-SHA52e candidate only. It does not instantiate51b or build either full canonical graph. `load_single_candidate()` releases its local PackedScene reference when returning the instantiated node, before live `_ready` and world streaming begin. Existing successful build/audit and baseline report files are verified by fixed SHA256 and reused as prior evidence.

## Parent-owned GUI launch

Run each subset separately in the existing cloud desktop terminal, after coordinating the shared rendering window:

- `python /workspace/scratch/a29d03198654/Aether/cloud-evidence/cloudsea52e-recovery-preparation/run_remaining52e.py close`
- After reviewing its terminal result: replace `close` with `climb`

No GUI process was started by this preparation worker. The runner uses a single-process lock and records true process return code, termination signal, Linux `RUSAGE_CHILDREN.ru_maxrss` inKiB, observed VmRSS/VmHWM samples, elapsed time, input hashes and logs. It does not diagnose an unknown termination from memory statistics alone.

The close process captures only three close views; climb captures only four staged camera stations and their three connecting segments. Every actual frame atomically checkpoints `partial-report.json`, including a pending-frame stage before image save and completed metadata after it. Existing source/scene/default/controller files remain immutable. These are camera observations, not player-controlled flight.

After both complete, pass their actual output directories to `summarize_recovery.py`. It pairs only the seven recovered actual metadata records against the existing51b records. The complete original pair stays failed because nine52e runtime rows were lost. Different fresh-process world-streaming histories are also not represented as proven identical live geometry; only recorded camera/environment values and the immutable saved scene are compared.

Prepared checks: Godot4.5.1 pure parse-v2 exit0; both Python files compile. No render or scene save was performed during preparation.
