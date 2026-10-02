# Cloud-bank design v2, bounded offline repair

Read `REVISION_NOTES.md`, then `rendered/RESOLVED_PROFILE.md` and the two corrected section diagrams. This closes only the three v1 internal design conflicts. No model, `.blend`, engine, world edit, Git or Slack action is included. Stop pending independent review and complete plugin publication/readback.

## One source of design values

`profile-definition.json` is the sole new authored section/junction definition. It SHA-binds the published v1 plan and reuses the unchanged A/B/C/D controls, 52 landmark semantics, original four camera records, anchor, material and weather. Shared top and lower intersections reference nodes; diagrams and generated records do not carry separate hard-coded profile geometry.

v1 remains rejected and unchanged at:
`source-assets/cloud-bank58/revision-l/design-v1`
Published parent: `b19400f1fdf4bb581e248f2389fb203c645a0808`.

The unmodified 02 plan, 05 landmark diagram/data and original footprint files are dependencies, not duplicated outputs. `dependencies.json` gives their verified identities. The old unlocated C inset is not reissued or certified as a spatially constrained section.

## Explicit reproduction contract

There is no sibling-directory assumption or automatic source discovery. All commands require:

- `--aether-root`: absolute root of the verified Aether checkout containing v1
- `--survey-npz`: absolute path to the exact restored checkpoint NPZ, SHA256 `33dd320034359f224d9fff0a5a9d43f1a51a5a770beaefefe6954c6c6b7c1615`
- Rendering additionally requires `--render-to`, which must be outside the Aether repository

The checkpoint NPZ may first be restored with its existing published helper. This revision never reruns `survey.py`, restores inputs implicitly or creates a model. Use a fresh output staging directory when reproducing a published package.

Check only, no output writes:

    PYTHONDONTWRITEBYTECODE=1 python revise_design_v2.py --aether-root /absolute/Aether --survey-npz /absolute/verified/survey-grids.npz

Generate the two offline diagrams and reports in external staging:

    PYTHONDONTWRITEBYTECODE=1 python revise_design_v2.py --aether-root /absolute/Aether --survey-npz /absolute/verified/survey-grids.npz --render-to /absolute/external/staging

Run the pure tests against those outputs:

    PYTHONDONTWRITEBYTECODE=1 python test_revision_v2.py --aether-root /absolute/Aether --survey-npz /absolute/verified/survey-grids.npz --rendered-dir /absolute/external/staging
    PYTHONDONTWRITEBYTECODE=1 python -O test_revision_v2.py --aether-root /absolute/Aether --survey-npz /absolute/verified/survey-grids.npz --rendered-dir /absolute/external/staging

Optional `--definition` explicitly selects the authoritative JSON; otherwise it is read beside the script. Inputs are verified before calculations. No engine dependency. Tested with Python 3.12, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8 and Pillow. Plot bytes can vary across fonts/library versions; never overwrite the delivered authoritative artifacts to force a match.

## Deliverables and verification

- `profile-definition.json`, `revise_design_v2.py`, `test_revision_v2.py`: authority, resolver/checker/drawing code, pure negative controls
- `rendered/03-central-volume-section-v2.png`, `rendered/04-near-shoulder-section-v2.png`: mathematical diagrams; not native geometry
- `rendered/RESOLVED_PROFILE.md`: generated values and exact shared anchor relationships
- `rendered/validation-report.json`, `final-validation-summary.json`: limited consistency results, clear exclusions, unchanged original gates
- `rendered/interval-audit.json.gz`: all1626 interval records; gzip of canonical UTF-8 JSON, raw size/hash in validation report; no missing raw payload
- `rendered/plot-trace.json`: actual plotted line arrays plus PNG hash/metadata identity
- `tests-normal.json`, `tests-optimized.json`:15 passing tests each; actual v1 conflicts remain rejected
- `REVISION_NOTES.md`, `README.md`, `dependencies.json`, `PACKAGE_MANIFEST.json`, `SHA256SUMS.txt`: scope, reproducibility and package identities

Runtime plotting/font caches under `rendered/runtime-cache/` are excluded; they are not deliverables. Every new content file is in the manifest. The checksum file also covers the manifest, but cannot recursively include itself.

The continuous claim concerns only numerical extrema of the two defined piecewise-cubic 1D curves. Outer/inner classification uses the finite archived5m cell representation and conservative within-interval motion bounds. It is not a directed-rounding proof or an analytic true-mesh distance result. Exact 3D contact, native shape, self-occlusion and pixels remain unproved.
