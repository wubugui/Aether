# Full-bank offline design, one bounded task

Design only. No `.blend`, mesh resource, world save, engine execution, Git operation or Slack delivery was made by this task. Stop after this package is handed to the parent. Upload and full remote byte readback must precede any further construction.

Read `DESIGN.md` for the complete Chinese design and acceptance plan; `design_plan.json` gives the seven bounded semantic controls, world anchor, intended crest/trough/belly structure, proposed topology and material contract.

## New deliverables

- `DESIGN.md`: full design, evidence limits, editable structure, separate coverage/interface gates, exact original camera rule and proposed front-frame domains
- `design_plan.json`: machine-readable design assumptions and future gates
- `02-proposed-bank-plan.png`: plan, actual archived outline/overlap masks versus new crown/valley assumptions
- `03-proposed-volume-sections.png`: D front shoulder through A/valley/B, and a different C side-return section, with a curved common belly
- `04-proposed-near-shoulder-section.png`: proposed A cross-section along the original near horizontal viewing direction
- `05-original-front-landmark-domains.png`: projected proposed crest/shoulder point domains, actual old-cloud ray hits, and the original frame's right edge
- `draw_design_schematics.py`: offline generator for diagrams 02/03/04; no mesh/engine construction
- `analyze_design_landmarks.py`: distinct bounded rays to NEW assumed landmarks and diagram 05; no rerun of the old footprint survey
- `design-landmarks.json`: 52 proposed landmarks projected with actual original front matrix, checked against eight saved indexed old-cloud meshes; not new-surface visibility
- `evidence-bindings.json`: input SHA/size, unchanged original survey identities, the four original actual camera byte records, and assumed crest-point projections
- `PACKAGE_MANIFEST.json`: identity and dependencies of the 11 content deliverables above
- `SHA256SUMS.txt`: SHA256 for all 11 content deliverables plus the manifest; it cannot include itself recursively

Four PNGs are labelled mathematical/offline diagrams, not actual screenshots. They were personally opened and inspected. No data, diagram or prose marks the new cloud as source-, world-, flight- or hardware-accepted.

## Preserved dependencies, not duplicated as new work

The four pre-HOLD survey files remain byte-identical to:
`cloud-evidence/cloudbank-next-footprint-checkpoint-20261002/{survey.py,survey.json,survey-grids.npz,01-existing-footprint-survey.png}`

Checkpoint commit: `6d2ae7909b8578ebdd7eaf407b707e1d3f74ebec`. NPZ is stored in that checkpoint as four plain Git chunks; use its existing `restore_grid.py --restore-missing` when needed. Do not rerun or adapt archived `survey.py` just to regenerate unchanged evidence.

Current design release was received after the parent verified `258e337886e72dd524749cfc3e683495853d9e81`. No private communication receipt is included here. Existing material/projection/reference paths and exact input SHA are in the evidence bindings. The changing `CLOUD_RESUME.md` hash is a read-time identity, not a request to freeze later project updates.

## Reproduction

Normal readers need only the Markdown, JSON and PNG files. Reproduction is optional and must respect the serial publication gate; it does not launch an engine.

1. Use a new staging directory outside the repository and place the new package's content there.
2. Materialize the exact preserved `survey-grids.npz` beside the scripts from the verified checkpoint; verify its recorded SHA. Diagram 02/03/04 only need this NPZ and `design_plan.json`.
3. Use Python with NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8 (the tested versions). `PYTHONDONTWRITEBYTECODE=1 python draw_design_schematics.py` generates the three diagrams. Script-local cache directories are implementation caches, not deliverables.
4. For the distinct sparse landmark query, set `AETHER_ROOT` to the actual Aether repository and run `PYTHONDONTWRITEBYTECODE=1 AETHER_ROOT=/absolute/Aether python analyze_design_landmarks.py`. It needs `design_plan.json`, the NPZ, `evidence-bindings.json`, the original `provenance58k.py` decoder, and the fixed saved `Game53dWest.tscn`. It projects the NEW assumed landmarks; it does not rerun the old grid survey.
5. Reproduction output bytes may change with plotting-library/font versions. Keep this delivered package as authoritative; do not overwrite it to force matching hashes.

Excluded from publication: `mpl-cache/`, `diagram-cache/` and other local plotting/runtime caches. The four old survey files are already published dependencies, not new edits. There are no new model artifacts hidden in those caches.

## Known limits

The original front is the comparison view. A is the primary planned visible crown; C is the right return; D has three landmark rays blocked by old 1_0. B's crest center is outside the front frame, while five proposed shoulder points are inside. Near A/D crest points are in-frame; near B/C centers are outside. No self-occlusion or non-cloud pixel visibility is proved because no candidate mesh exists. Exact original camera matrices are preserved; never recompute side/near from the new bank's bounds center.
