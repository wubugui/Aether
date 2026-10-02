# JSON decimal diagnosis 01, source reproduction only

The original failed collection is unchanged:
`cloud-evidence/north-ridge62-scatter-collect-20261002T062426Z-j_zfldme`.
Its raw JSON printed the compared numbers at default precision and did not retain
raw float64 bits. No later calculation can recover those missing historical bits.
This diagnosis explains the failure from the exact pinned source and independent
input; a fresh lightweight Godot witness is still required.

Seven full MIT-licensed upstream snapshots are SHA-bound in
`upstream/source-manifest.json`. The official `4.5.1-stable` tag resolves to commit
`f62fdbde15035c5576dad93e586201f4d41ef0cb`, matching the pinned binary's version.
No engine was launched and no world or asset was modified.

## Exact source chain and reproduced discrepancy

- `core/io/json.cpp`, `_get_token`: JSON numbers become a double from
  `String::to_float`; `_stringify` uses `p_full_precision ? 17 : 14`
- `core/string/ustring.cpp`, lines 2383–2600: `built_in_strtod` collects two integer
  mantissa parts, computes `(1.0e9 * frac1) + frac2`, constructs a decimal exponent
  and divides/multiplies in binary64. `String::to_float(char32_t...)` calls it
- `core/variant/variant.h` stores scalar FLOAT in `double _float`; default
  `real_t` in `core/math/math_defs.h` is float. Actual runtime format is also gated
  by the 52-byte Transform3D native encoding, not assumed from this default alone
- `core/io/marshalls.cpp` writes Transform3D basis ROWS, then origin. This native
  Variant byte order is distinct from the explicit column/origin comparison order
- `core/crypto/hashing_context.cpp` rejects `update` when byte count is zero;
  `start` and nonempty `update` return Error; `finish` returns empty bytes on error

`reproduce_json_decimal.py` extracts the exact unmodified `built_in_strtod`
template into a temporary standalone C++ harness, compiles it with installed g++
(`-O0 -ffp-contract=off`) and feeds all 9,300 numeric tokens in the original 775
prepared transforms. It does not translate the arithmetic into another parser.
Its compiler and executable are temporary; `SOURCE_REPRODUCTION.json` retains
function/harness hashes, return codes and every binary64 difference.

All 9,300 results convert back to the exact source-oracle binary32 bytes. Five
binary64 values differ from the exact binary32 lifted to double. The first is the
original failure's World/Vegetation/Authored_WestRoadCopse component 10 (origin Y):

- Original prepared token: `14.084564208984375`
- Exact saved binary32: LE bytes `605a6141`
- Exact binary32 lifted to double: LE `000000004c2b2c40`
- Exact source-reproduced JSON double: LE `010000004c2b2c40`
- Difference: +1 binary64 ULP, `1.7763568394002505e-15`

Prepared X and Z have no such difference. Four later prepared rows also exhibit
one-binary64-ULP transport differences, listed in the report; the failed native
collection did not reach them. The source reproduction is not proof they have
already passed a native collector.

The minimal correction and fresh 18-case Godot fixture are in sibling
`scatter-float32-correction-01`. They preserve the old metadata and old failures,
retain raw byte witnesses, and compare exact binary32 identities without epsilon.
