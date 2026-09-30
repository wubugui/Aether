# Candidate42d allocation fix preparation

## Scope

New scripts only; no scene was built in this preparation run. Game42c and historical evidence remain unchanged. The builder derives from preserved Game42b and repeats the original 42c mesh scaling, shader, and deterministic placement; only MultiMesh copying changes. Existing world, weather controller and project default are not edited.

The two historical `build-42c-1754.stderr.log` errors point to `MultiMesh.duplicate()` at `build_particle42c.gd:15`, before mesh scaling. Godot 4.5 documents that instance_count allocates/clears buffers and format flags must be configured before it. The new helper therefore explicitly sets format/flags, allocates once, copies each transform and enabled color/custom payload via typed getters/setters, and restores visible count. This avoids Resource.duplicate() property-copy ordering dependence.

Official documentation: https://docs.godotengine.org/en/4.5/classes/class_multimesh.html

## Tests and honest limitations

Official Godot 4.5.1 stable was used. The initial headless runtime test parsed and ran with empty stderr but reported 74/100: all 24 nonempty synthetic buffer-size cases and two nonzero actual-source custom-data checks failed. Headless dummy rendering does not provide the required MultiMesh storage; equality of two empty/default getter results is not evidence of a successful copy. This failure is retained as `test.stdout.log` / `test.stderr.log`.

The new builder, unit test and verifier now refuse headless execution before copying/building. Their independent `--headless --check-only --script` parses all exited 0 with empty stderr. No graphics validation or visual acceptance is claimed.

Next, under a real rendering server with the official 4.5.1 runtime:

1. Run `res://tools/test_multimesh_copy42d.gd`, requiring 100/100 and empty stderr
2. Run `res://tools/build_particle42d.gd`; it refuses an existing Game42d scene
3. Run `res://tools/verify_weather42d.gd -- --output-dir=/absolute/new/path`; no project default change is needed

The verifier checks serialized 42d allocation/payloads against 42b, initial transforms and mesh bounds against 42c, actual expected rain/snow transform motion and deterministic seek, and all retained native-world checks. Four extra paired-time captures support review but do not independently establish visible precipitation or full visual fidelity. Its checks-only mode requires a rendering server and avoids the inherited missing-image reads.

Preserved Game42c SHA256: `06f86e4bc73ed2d28a4eb6d76e89e3946cb6b6c6e7e72b9b36f55ed972880c91`.

## Follow-up: historical buffers missing (19:08 UTC)

The non-headless Godot 4.5.1 Compatibility test using Mesa llvmpipe passed all 96 synthetic copy/allocation checks plus both actual-source equality checks, but failed both assumed nonzero source custom payload checks (98/100). Inspection established that both weather MultiMesh subresources in both Game42b and Game42c have only `transform_format`, `use_custom_data`, `instance_count`, and `mesh`: their saved buffer/transform/custom-data properties are absent. Thus the historical zero payload is real, not solely an effect of the headless renderer. The original scenes remain untouched; this defect plausibly contributes to missing precipitation because absent transform buffers create degenerate particle transforms.

The next additive revision explicitly recovers authored custom payloads from the exact `build_weather42b.gd` RNG sequence (seed `4200+count`, consume X/Z draws before each custom draw), and initial transforms from the exact `build_particle42c.gd` RNG sequence (`4242+count`). The generic copy helper still preserves whatever source payload exists and is tested independently with nonzero synthetic transforms/colors/custom data. No original scene is silently rewritten.

The two erroneous nonzero-source assumptions were replaced by assertions that the reconstructed actual Rain/Snow payloads are nonzero and transforms nondegenerate. The builder now reloads its output with CACHE_MODE_IGNORE and requires the complete serialized buffer to equal its in-memory buffer float-for-float, plus nondegenerate basis. The full verifier compares all transforms and custom payloads to the original authored seeds, not the defective historical empty buffers. These changes remain subject to actual rendered execution.

The rendered test also emitted an unsupported VSync warning and two texture-leak errors on immediate process exit. The retry explicitly disables VSync and defers quit until eight frames after local resource references leave scope. No stderr is silently ignored by the wrapper.
