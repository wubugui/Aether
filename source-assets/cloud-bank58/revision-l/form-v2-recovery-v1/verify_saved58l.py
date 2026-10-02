"""Only open the exact existing source and exercise it in memory. No save path."""
from __future__ import annotations
import argparse, os, sys, traceback
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import recovery58l as r


def main(arguments=None):
    args = arguments if arguments is not None else (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['verify'])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--admission', type=Path)
    a = parser.parse_args(args)
    if a.mode is None:
        print('No-op: existing-source recovery needs a new bounded admission.')
        return 0
    r.require(a.out is not None and a.admission is not None, 'Explicit recovery admission/output')
    runtime = r.runtime(native_process=True)
    r.verify_admission(r.read(a.admission), a.admission, a.out)
    r.require_source()
    n, s, g = r.native, r.s, r.g
    n._TELEMETRY = (a.out, 'verify')
    n.emit('native_entry', mode='verify', recovery_stage=r.STAGE, recovery_version=r.VERSION)
    report = dict(acceptance_mode=s.DIAGNOSTIC_MODE, full_native_acceptance=False, diagnostic_acceptance=False,
                  historical_default_failure=dict(s.HISTORICAL_DEFAULT_FAILURE), version=g.VERSION,
                  recovery_version=r.VERSION, recovery_stage=r.STAGE, original_source_stage='failed',
                  admission_sha256=r.sha(a.admission), runtime=runtime, mode='verify', view=None, pid=os.getpid(),
                  passed=False, state='started', source_saved=False, images=0, world_loaded=False,
                  world_integration_allowed=False, contact_acceptance=False, world_acceptance=False,
                  global_GOAL=False, visual_acceptance=False, weather_acceptance=False)
    try:
        import bpy
        c, b = r.read(g.CANDIDATE_PATH), r.read(g.BINDING_PATH)
        n.emit('candidate_validation.begin'); g.validate_candidate(c); n.emit('candidate_validation.complete')
        n.emit('fresh_open.begin')
        bpy.context.preferences.filepaths.use_scripts_auto_execute = False
        bpy.ops.wm.open_mainfile(filepath=str(g.SOURCE), load_ui=False, use_scripts=False)
        n.emit('fresh_open.complete', opened_filepath=bpy.data.filepath)
        r.require(Path(bpy.data.filepath).resolve() == g.SOURCE.resolve(), 'Actually opened exact existing source')
        r.require_source()
        raw = n.capture(c, g)
        path = a.out / 'verify-raw.json'
        n.write(path, raw, True)
        report.update(raw_path=str(path), raw_sha256=r.sha(path))
        n.write(a.out / 'verify-result.json', report)
        report['validation'] = g.validate_native_raw(raw, c, b)
        # Original g.HERE remains form-v2, so all eight saved Texts use ORIGINAL bytes.
        baseline = r.read(r.OLD_RUN / 'outputs/build-raw.json')
        r.require(s.identity(raw) == s.identity(baseline), 'Complete saved build/fresh-open numeric identity')
        probes = n.exercise(c, b, g, raw, a.out, 'verify')
        report.update(controls_exercised=7, secondary_exercised=sum(len(x.get('secondary_parameters', [])) for x in c['controls']),
                      manual_edit_exercised=True, exercise_sha256=r.sha(a.out / 'verify-exercise.json'),
                      exact_identity_restored=all(p['exact_identity_restored'] for p in probes))
        r.require_source()
        report.update(passed=True, diagnostic_acceptance=True, state='completed', source_sha256=r.SOURCE_SHA, source_bytes=r.SOURCE_BYTES)
    except BaseException:
        report.update(state='failed', error=traceback.format_exc())
        try:
            path = a.out / 'verify-failure-raw.json'
            n.write(path, n.capture(c, g), True)
            report['failure_raw_sha256'] = r.sha(path)
        except BaseException:
            report['failure_capture_error'] = traceback.format_exc()
        raise
    finally:
        n.emit('native_terminal', passed=report['passed'], state=report['state'])
        n.write(a.out / 'verify-result.json', report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
