# North ridge62 restored-source read preparation

Status: preparation and pure checks only. This directory has not launched Blender/Godot, restored or copied a native source, rebuilt, saved, or rendered. Independent review and the local preparation freeze are recorded alongside this README; the single native admission still requires parent scheduling. No existing recovery-v2 file, native source, raw report, helper, or project is changed.

## Authority and exact restoration layout

The successful actual source run is `cloud-evidence/north-ridge62-recovery-v2-source-20261002T114825Z-lnt78w53`. Its existing `native-storage.json` and `restore_native.py` are pinned, read-only inputs. The restoration contract is the existing helper's `--destination-root` behavior: retain the complete repository-relative paths under the chosen root. The probe never invokes that helper and never creates/restores native inputs.

The restore root must contain exactly the manifest's four files and the directories needed for those paths: the 10,004,835-byte `.blend`, 14,837,932-byte actual build raw, 14,837,933-byte actual verify raw, and 5,424,727-byte embedded binding input. Every size and SHA-256 must match. Extra files, extra empty directories, missing files, symlink files/ancestors, hardlinks, nonabsolute/traversal paths, original-repository roots/ancestors/descendants, and source paths other than `ROOT/source-assets/north-ridge62-authoring/recovery-v2/north-ridge62.blend` are rejected.

Original and restored source SHA-256: `dd1d3c12b8c3f98fdcd42a21057d519f1cac48eeab468cbc7721d1c1673ab502`.
Actual original build-raw SHA-256: `c941a75a43a5c4f88d4083c403cb9f3219752c49056405bed66840803b0f629b`.

## Read-only implementation

`probe_restored62.py` opens only the explicit `--restored-source`, with `load_ui=False`, `use_scripts=False`, and wrapper `--disable-autoexec`. Actual `bpy.data.filepath` must equal that exact restored path. It directly reuses frozen recovery-v2 `native62.capture` and `contract62.validate_raw`; it neither copies their logic nor modifies module globals. Complete actual raw is written and hashed before validation. Every original validation gate remains, then the entire raw dictionary must equal the original actual build raw except the two top-level process fields `pid` and `cpu_affinity`. Freshness comes from this one-shot wrapper's new process launch and actual wait4 PID matching both terminal/raw, together with the exact restored opened filepath and new evidence-run identity. Historical numeric PIDs can repeat across runs/namespaces and are intentionally not compared for inequality. No native save, rebuild, render, world loading, or acceptance is present.

The wrapper directly reuses the original `bounded_support58k.run_child` and `run_import58k.file_manifest`, retaining actual PID, wait4, CPU2, 1.5GiB aggregate RSS, timeout, kill/reap, and original lifecycle reports. There is one native child, capped at 30 seconds within a 60-second wrapper, with 8 seconds reserved for final checks. The original source-assets (including canonical recovery-v2 `.blend` and all old attempts/terminals), blender/assets/ref, project.godot, entire actual main project including caches, and original successful evidence run are protected before/after by complete file SHA and directory membership. The restored four-file tree gets the same before/after protection. No recovery-v2 mutable exclusion is inherited.

One exclusive new `restore-read-attempt.json` is created in this directory before protection is snapshotted. It is not a success report and blocks every repeat, including after failure. Evidence and the terminal wrapper report are written only to one new `cloud-evidence/north-ridge62-restore-read-v1-*` run. No retry, source replacement, artifact deletion, automatic restoration, or render fallback exists.

## Pure commands (no engine)

From the Aether root:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/restore-read-v1/test_restore_read62.py
    PYTHONDONTWRITEBYTECODE=1 python -O source-assets/north-ridge62-authoring/restore-read-v1/test_restore_read62.py
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/restore-read-v1/run_restore_read62.py

After parent remote byte verification and clean reconstruction, default mode can check the actual existing reconstruction without opening it. Parent has supplied this specific root; arguments stay explicit rather than being hardcoded into the probe:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-authoring/restore-read-v1/run_restore_read62.py --restore-root /tmp/aether-native-reconstruction-z_1vwkc3/restored --restored-source /tmp/aether-native-reconstruction-z_1vwkc3/restored/source-assets/north-ridge62-authoring/recovery-v2/north-ridge62.blend

Pure fixture tests create only tiny synthetic text bytes in temporary subdirectories of this new preparation directory; these are not actual native restorations. Real raw-validator tests read the original raw as JSON without a native engine. No test calls `restore_native.py`, copies the actual `.blend`, or runs Blender.

## Later reviewed one-shot admission (DO NOT run during preparation)

Parent independently reviews this source, finishes pure checks, and writes `FINAL_SHA256.json` using the existing repository-relative `files` mapping with each file's `sha256` (and optionally `bytes`). It must include every `.py` in this directory and this README; the wrapper verifies all entries and includes the freeze itself among protected inputs. FINAL_SHA256.json is supplied in the completed preparation and must remain unchanged. The default preflight validates it when present; native admission requires it.

Only after that review/freeze, remote byte verification, actual clean restoration, and parent resource scheduling, append `--run-approved` to the exact explicit-path default command above. Do not invoke the probe directly. Other source/project writers must remain paused through the original/restored before/after checks. A passing native read proves storage reconstruction and exact native source readback only; it does not prove view images, support acceptance, world integration, performance, or the complete goal.
