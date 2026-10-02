# Independent source review: shadow-script-v4

A separate read-only reviewer examined the original v3 parser failure, v4 collector and wrapper, immutable bindings, copy hierarchy, and focused tests. The reviewer made no edits and started no engine.

Result: no source-level blocker found. The reviewer confirmed:

- Exactly one native block replacement; reversing it reproduces frozen v3 byte for byte
- `get_script()` result is Variant, explicit `is Script` check precedes the typed cast and resource-path access
- Original helper source SHA check is retained, and helper/request bytes are unchanged
- V3's schema and analyzer are reused directly; all inherited version/source and geometry proof gates remain
- Main launcher differs only in two output/status labels; five native launch inputs, relative inheritance, single CPU2/60s bounded launch, dependency guard, before/after file checks, and failure flags remain
- Complete v3 frozen sources and original failed-run evidence are SHA-bound
- Independent executions of all 72 groups passed under normal Python (0.613s) and optimized Python (0.644s)

These are source/pure-test results. Native GDScript parsing, mesh reading, runtime collision, and full occupancy are not certified by this review. The parent schedules the only actual native run.
