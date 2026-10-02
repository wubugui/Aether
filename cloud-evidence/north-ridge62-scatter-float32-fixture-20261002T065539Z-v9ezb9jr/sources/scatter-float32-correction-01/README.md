# Saved scatter correction 01: exact binary32 identity

Preparation only. No Godot parse, fixture or collection has run for these sources.
The original `scatter-readonly-v1` directory, all 28 frozen files, both prepared
metadata representations and every original failed/successful native run remain
unchanged. Parent owns publication, engine/window coordination and CLOUD_RESUME.

## Narrow correction

The collector is a minimal copy of v1: checked hashing, explicit transform byte
identity/witnesses and full-precision JSON output are changed. SceneState merge,
ancestor composition, instance swizzle, buffer and mesh checks, source authority,
query/design boxes, spatial intersection logic and limitation flags remain.
The original metadata is read directly from v1 and reconstructed from its exact
source inputs before launch, with raw SHA
`827e5618b5f4d1ea22a7e789f6ad1fbc1aa80daa5d98de2bac4ff00553518b8c`.

A small `transform-float32-identities.json` sidecar binds that original SHA and
all 775 path-specific ordered 48-byte identities. It is independently generated
from the original Python float32-step oracle. It contains no instance buffers.
The wrapper requires exact rebuilt sidecar content and serializes the same bytes
for the child. The child checks the original metadata SHA and complete path set;
its report binds the sidecar SHA too.

For every group, the collector checks exactly 12 finite components, in order:
three basis columns (XYZ each), then origin XYZ. It checks numeric types and
rejects binary32 overflow before comparison. It then requires:

1. Native components already equal their binary32 values, bit for bit after
   lifting back to binary64. A nonrepresentable native double cannot be silently
   rounded into agreement
2. Native binary32 bytes equal the independent canonical sidecar bytes exactly
3. JSON-parsed expected values convert to those same canonical bytes exactly

The full 48 bytes are compared, not only the SHA. Signed zero bits are retained.
SHA256 fingerprints are additional evidence, not a substitute for exact equality.
Each fresh group records actual binary32 bytes, parsed-expected and independent
binary32 bytes, actual/parsed-expected binary64 bits, fingerprints, ordered layout,
component count and explicit transport-double equality. Every exported transform
also retains exact binary32/binary64 bytes and native Variant bytes. The Python
validator decodes native Transform3D row-major bytes and checks they agree with
its separate column-major fields and bytes.

## Why no representable mismatch can be hidden

The domain is ordered finite IEEE binary32 transforms, established by the pinned
engine, finite/count/type checks, exact raw Transform3D width and the explicit
native-already-binary32 check. Converting any member of that domain to binary32 is
the identity function. Distinct binary32 bit patterns therefore remain distinct,
including either neighboring representable value and signed zero. Ordered byte
comparison cannot accept a one-ULP change, transpose or component permutation
unless the transform was actually unchanged. The independent expected sidecar
prevents arbitrary JSON rounding from becoming a new source baseline. No spatial
boundary, distance threshold, oracle composition or production epsilon is changed.

This does not assert arbitrary double values are interchangeable: non-binary32
actual values explicitly fail, including the reproduced one-binary64-ULP value.
The conversion of expected JSON is only verified transport recovery of a separate,
fixed source identity. Source hashes and the original prepared metadata remain
required on every run.

## Empty SHA and terminal behavior

`start` must return OK. Empty input goes directly from start to finish; nonempty
input calls update and requires OK. Finish must yield exactly 32 bytes. Failures
append issues; the strict existing ERROR/SCRIPT ERROR/parse/leak log gate remains
unchanged. The inherited generic digest now uses this same checked helper.
No error log is hidden, excluded or retroactively removed.

The wrapper retains one child per explicit command, original 60-second process
limit, first two CPUs, exact pinned binary, full 1,483 dependency/startup/cache/
absence guard and all 1,477 historical inputs. Fixture failures, post-run guard
failure, changed source, exceptions, signal/timeout and wrong check sets all keep
success false. No main scene/world is started.

## Tests and future commands

- Original 173 Python cases run unchanged, normal and `-O`
- Extended 231 Python cases retain all prior cases and add raw-byte/schema/source
  failures: each of 12 one-binary32-ULP edits, signed zero, transpose/origin reorder,
  finite/type/count checks, missing raw evidence, malformed schema and hash guards
- Original 14 decoder test groups plus all 708 real resources and five standalone
  meshes run unchanged, normal and `-O`
- `check_float32_native.gd` prepares 18 native cases, including exact reproduction
  of the observed JSON double difference, empty/nonempty SHA, 1-ULP basis/origin,
  transpose, reordered origins, bad layout/types/finiteness/overflow, sub-binary32
  actual change, corrupt expected bytes and the nonsymmetric native row encoding
- Standalone compiled pinned-source decimal reproduction is in diagnostic-01;
  neither it nor Python tests is a Godot pass

After publication and explicit parent coordination, from Aether:

    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-float32-correction-01/run_scatter62.py --static-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-float32-correction-01/run_scatter62.py --parse-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-float32-correction-01/run_scatter62.py --fixture-parse-only
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-float32-correction-01/run_scatter62.py --fixture
    PYTHONDONTWRITEBYTECODE=1 python source-assets/north-ridge62-intake/scatter-float32-correction-01/run_scatter62.py --collect

Do not launch collection before both parses and the lightweight fixture pass.
The fixture explicitly says world_loaded=false/native_collection_passed=false.
A future collection only covers undeformed saved bound-mesh metadata AABBs.
Vertex-payload extrema, shader envelopes, runtime generated/model_scene/collision
geometry, road width, all occupancy and visual acceptance remain unproved/false.
