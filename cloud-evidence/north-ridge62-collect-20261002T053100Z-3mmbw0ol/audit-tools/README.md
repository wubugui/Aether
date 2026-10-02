# Frozen audit source tools

These are the actual Python sources embedded in `audit_method` of the pinned
`DEPENDENCY_REVIEW.json.gz`. They were inspected before copying and are preserved
byte-for-byte, including original absolute paths. Neither includes geometry or
scatter payloads. The runtime guard uses only Python's standard library and does
not execute these audit sources.

| Source | Original path | Bytes | SHA256 |
|---|---|---:|---|
| `audit_north62_deps.py` | `/tmp/audit_north62_deps.py` | 6884 | `7efbb80f98581453faaaa6b8c3fc70c0d4747848f1778bb13676d1130ca72f5a` |
| `north62_binary_review.py` | `/tmp/north62_binary_review.py` | 4624 | `f89c31a863550f75bc18de17804f1157e843fde1dc096986afac21fcf0fee448` |

The graph source reads the current project and writes its provisional metadata
graph to `/tmp/north62-dependency-graph.json`. It is deliberately the original
first-pass source: its five RSCC-header gaps and binary `script`-property-name
flags require the subsequent full binary inspector. Running that source alone
does not reproduce the final audit conclusion.

The binary module exports `inspect(path)`. It uses already-installed `zstandard`
for RSCC mode 2; do not infer that the standard-library runner needs this package.
For a full replay, run the graph source, import this module, call `inspect` on
every `.res`, `.mesh` and `.scn` in the graph's `files`, require zero exceptions,
zero nonnull `script_properties` and zero `legacy_inline_external_refs`, then
compare the returned dependency tables, native classes and stream-boundary
results with the pinned review. The five imported scenes must also have zero
external dependencies. Literal script inheritance/preloads, attachment ownership
and importer settings still require the source review described in
`DEPENDENCY_REVIEW.md`; neither historical script is a general GDScript parser.

For a relocated checkout, adapt paths only in a separate working copy and write
new evidence to a new output directory. Do not overwrite the frozen JSON or old
preparation evidence. The original report-assembly utility
`/tmp/freeze_north62_dependency_review.py` is not embedded in `audit_method` and is
not required by the guard; it expects the original pre-v2 preparation identities
and must not be used to silently regenerate this frozen review.

The new `dependency-guard-v2` fixture checks AST syntax, original/embedded byte
equality and positive/negative identity checks without running these auditors or
any Godot/Blender executable.
