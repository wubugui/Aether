# Proxy bounds: structured engine-version guard v2

Source preparation only. No engine, terrain/scene/asset writes, new downloads, Git, progress-document or Slack actions were performed for this supplement.

## What failed

The first actual v1 read is preserved at `cloud-evidence/north-ridge62-proxy-bounds-v1-20261002T081935Z-ppkqotra`: child exit 2, wrapper failed, 0.454313382 s, no engine log errors or changed inputs, zero visual meshes read. Its sole issue was `fixed engine version`. The v1 prefix check expected `4.5.1.stable.official`; it did not record the observed dictionary before rejecting it.

The previous completed native GL fixture at `cloud-evidence/nearbay61-continuous-v6-20261002T064755Z-ip7pcsa8/result.json` records the actual structured version:

- major 4, minor 5, patch 1
- status `stable`, build `official`
- full commit hash `f62fdbde15035c5576dad93e586201f4d41ef0cb`
- hex 263425, timestamp 0
- display string `4.5.1-stable (official)`

That result has SHA256 `07384bbd9e1f74d48f67a1132a81e9f746db3c8182f9379aacbc69860542d8aa`. Its independently pinned successful wrapper binds it to the unchanged binary SHA256 `db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199`. Replaying the old string predicate against this recorded dictionary is false. The old failure is not rewritten as success.

## Narrow correction

`read_proxy_meshes62_v2.gd` inherits the unchanged v1 collector and overrides only `_initialize`, adding a structured version-check helper. It records the full observed engine dictionary in the result before checking any field. Missing, extra, wrong-type and wrong-value fields produce field-specific diagnostics; every failure calls the inherited report writer before quitting. All nine fields are exact, including the full commit hash. No banner parsing, prefix match or shortened hash is accepted.

The v1 mesh readers, first-imported-rock semantics, six visual identities, query geometry and protection rules are unchanged. The v2 request is an exact derivative of the old request except its obsolete version-prefix field is replaced by the structured expectation and policy label. Native validation uses fixed source constants; the JSON request cannot weaken the engine gate.

The Python schema independently checks the same observed dictionary and diagnostic result before applying every original mesh-report check. The new wrapper uses the same fixed-binary SHA check, full dependency closure, isolated XDG, log-error rejection and one-process CPU2/60-second launcher. Both copied GDScripts and the request are hash-checked before/after execution. It preserves engine observations and diagnostics even for a future child failure at this guard.

## Verification and preservation

- 29 pure Python test groups pass in normal and `-O` modes: all 18 original tests plus 11 structured-version/provenance tests
- Negative cases cover every missing/wrong-value/wrong-type field, shortened or altered hashes, misleading display prefixes, extra fields, missing/forged observations, changed expectations and retained malformed-mesh rejection
- Source checks verify the GDScript/Python expected dictionaries are identical, observations precede checks and mesh reads, and only initialization/version checking is added
- `provenance.json` pins 16 prior files, including the first failure, the positive native version observation and wrapper, original freeze, and parent-created raw/gzip/storage files
- Original v1 freeze SHA remains `95158efd63c46c8760f8df2c214524a2c5132c9a908a3ea69747c481d421e48f`
- The original `source-bounds-preparation.json` bytes and parent's gzip/STORAGE packaging remain unchanged; no restoration or rewrite occurs here

Neither this v2 GDScript nor its native branch has been parsed or executed. Pure tests are not new native proof. All occupancy/runtime/visual-completion limitations remain false.

## Later command, only when scheduled

From Aether:

`PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/proxy-bounds-v1/version-guard-v2/run_proxy62_v2.py --collect`

Without `--collect`, this command performs source/preparation checks only. The scheduled command runs exactly one native read with the original two-CPU/60-second bound and writes a new `north-ridge62-proxy-version-v2-*` evidence directory. No original failed output is overwritten and no automatic retry is configured.
