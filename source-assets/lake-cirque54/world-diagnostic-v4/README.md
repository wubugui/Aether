# Original ArrayMesh lifetime control

Actual v3 run `cloud-evidence/cirque54-material-phase-v3-20261001T084931Z-kpkogfdr` returned child 0 / strict wrapper 1. Eight temporary meshes were fully freed while the original material remained valid without errors; the same four null-material errors occurred only at `cleanup.before_queue_free`, at about 66.38 seconds.

Successful 53d temporary-world and 55 observation scripts do not hold the original cirque ArrayMesh in a separate local variable across full-world deletion. Failed 54 v2/v3 do hold `original_root_mesh`, solely to verify preservation. This is an observed code difference, not a proven cause.

This v4 is exactly v3 plus `original_root_mesh = null` after all preservation checks, report writes and temporary-mesh retirement, before full-world deletion. Same rejected v1 source, same one original 1128 view, same material constructor, same scene and remaining cleanup order. Phases immediately before and after the one reference release let the actual renderer distinguish that release from full-world deletion. No thresholds or log gates change.

Run only in the parent-scheduled graphical terminal:

`python source-assets/lake-cirque54/world-diagnostic-v4/run_material_phase_probe.py`

Actual v4 run `cloud-evidence/cirque54-material-phase-v4-20261001T090140Z-vtews80k` passed child0 / strict wrapper0 in74.687 seconds, with no ERROR/leak, all frozen inputs unchanged and only the known VSync warning. This supports the scoped same-source cleanup ordering correction. It does not establish an initialization defect, a general engine-wide conclusion or shape acceptance. No old-v1 rerun is needed.
