# North-ridge62 shadow Script-path compatibility v4

Source-only supplement for the one v3 parser failure. The original v1/v2/v3, their freezes, and every actual failed run remain immutable. No engine was invoked to prepare this supplement. Native parsing and mesh collection are still unverified.

## Observed failure

`cloud-evidence/north-ridge62-shadow-arrays-v3-20261002T092937Z-rurh4rw7` ended in 0.505774034987553 seconds, child/wrapper exit 1. The parser rejected `ShadowAudit.resource_path` because `ShadowAudit` is a preloaded script class. The collector did not load and produced no native mesh report. Both original engine errors, the complete failure terminal, and its unchanged-input result are retained and SHA-bound in `provenance.json`.

## Sole native change

`read_proxy_meshes62_v4.gd` instantiates the existing auditor, obtains `auditor.get_script()` as Variant, checks `is Script`, casts to the explicit Script type, then obtains that instance's `resource_path` for the original full SHA check. The checked helper is the byte-identical existing `visible_geometry61.gd`, SHA:

`966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7`

`exact_collector()` enforces the entire native file equals frozen v3 after this one block replacement. The inherited version gate, six source-specific visual identities, first imported rock binding, strict shadow decoder and all-LOD oriented triangle proof, indexed bounds, actual snapped `get_faces` witness, conservative union, and full-precision JSON are otherwise byte-for-byte unchanged. There is no new geometry schema: the v3 request is copied unchanged and the original validator/analyzer modules are reused directly.

The wrapper's `main()` equals v3 after exactly two status/output-directory label substitutions. It retains the existing single process-group launch, CPU affinity two, 60-second limit, fixed binary SHA, full dependency guard, original/copied-input before/after checks, and terminal/error preservation. V3's complete frozen file set is additionally bound into the guarded inputs. Copied native inheritance remains `shadow-script-v4/` → sibling `version-guard-v2/` → original root script; the unchanged helper sits beside v4.

## Pure verification

72 groups pass with both normal Python and `-O`: the original 60 plus 12 focused checks. These include exact reverse-diff identity, typed instance lookup order, rejection of the old static expression, missing/weakened type or SHA gates, unrelated geometry/version/serialization changes, launcher/protection changes, immutable v3/failure bindings, unchanged request/schema, and copied inheritance layout. Source checks cannot prove native GDScript parsing; no success is claimed before the separately scheduled native run.

From repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-script-v4/test_script_path62.py
PYTHONDONTWRITEBYTECODE=1 python -O source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-script-v4/test_script_path62.py
PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-script-v4/run_shadow62_v4.py
```

Default wrapper operation is source-only, including the original saved all-group replay. It starts zero engines. Its normal and optimized outputs must match byte for byte.

## One later authorized native read

Only after the parent allocates the engine window:

```sh
PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/shadow-script-v4/run_shadow62_v4.py --collect
```

This remains the same one ≤60-second, two-CPU bounded read of six visual mesh identities and the runtime rock source, then the existing path/index keep/reconcile replay. Stop on any failure; no automatic retry, download, world audit, terrain modification, or runtime/full-occupancy proof is introduced.
