#!/usr/bin/env python3
"""Read-only replay of preserved build evidence; stdout only, no engine launch.

This does not replace the failed wrapper, change a validator, or claim fresh-open.
Run with Python -B; redirect stdout only to a new diagnostic result in this run.
"""
from __future__ import annotations
import hashlib, json, math, os, sys
from pathlib import Path
sys.dont_write_bytecode = True
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[1]
HERE = ROOT / 'source-assets/cloud-bank58/revision-l/form-v2'
OUT = RUN / 'outputs'
sys.path.insert(0, str(HERE))
import geometry58l as g
import native_support58l as s

def read(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def check(ok, message):
    if not ok:
        raise ValueError(message)

def diffs(a, b, path=''):
    if isinstance(a, dict) and isinstance(b, dict):
        result = []
        for key in sorted(a.keys() | b.keys()):
            if key not in a or key not in b:
                result.append(dict(path=path+'/'+key, kind='key_presence'))
            else:
                result += diffs(a[key], b[key], path+'/'+key)
        return result
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [dict(path=path, kind='list_length')]
        return [row for i, (x, y) in enumerate(zip(a, b)) for row in diffs(x, y, path+'/'+str(i))]
    if a == b:  # The original whole-raw identity is numeric equality, not JSON bytes/types.
        return []
    row = dict(path=path, native=a, replay=b)
    if type(a) in (int, float) and type(b) in (int, float):
        row.update(abs_difference=abs(a-b), ulps=abs(a-b)/max(math.ulp(a), math.ulp(b)))
    return [row]

def wanted_state(control=None, field='value', value=None):
    state = {r['id']: r['default'] for r in c['controls']}
    state.update({r['id']+'.'+p['id']: p['default'] for r in c['controls'] for p in r.get('secondary_parameters', [])})
    if control is not None:
        state[control if field == 'value' else control+'.'+field] = value
    return state

def hash_check(mapping):
    errors = []
    for path, expected in mapping.items():
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        digest = expected['sha256'] if isinstance(expected, dict) else expected
        if not p.is_file() or p.is_symlink() or sha(p) != digest:
            errors.append(str(p))
        elif isinstance(expected, dict) and p.stat().st_size != expected['bytes']:
            errors.append(str(p)+':size')
    return dict(count=len(mapping), all_match=not errors, errors=errors)

c, b = read(HERE/'candidate.json'), read(HERE/'bindings.json')
expected = s.expected_texts(HERE, c, b)
native = read(OUT/'build-result.json')
base = read(OUT/'build-raw.json')
probes = read(OUT/'build-exercise.json')
before_bytes = {str(p): sha(p) for p in OUT.rglob('*') if p.is_file()}
before_bytes.update({str(HERE/'cloud_bank58l_form_v2.blend'): sha(HERE/'cloud_bank58l_form_v2.blend')})
rows = []

def capture(path, recorded, state, manual_base=None, complete=False):
    raw = read(path)
    check(raw['pid'] == native['pid'] == 8, 'Actual build PID')
    check(raw['cpu_affinity'] == base['cpu_affinity'] == [0, 1], 'Actual CPU2')
    check(s.state_values(raw) == state, 'Actual complete prescribed control/secondary state')
    validation = g.validate_native_raw(raw, c, b) if complete else s.validate_capture(raw, c, b, expected, manual_base=manual_base)
    geometry = validation['geometry'] if complete else g.validate_evaluated(c, [s.world(v) for v in raw['mesh']['vertices']], s.state_values(raw))
    normal = validation['normals']
    differences = diffs(recorded, validation)
    rows.append(dict(file=path.name, sha256=sha(path), bytes=path.stat().st_size,
                     validation_replay_returned=True, actual_geometry_passed=geometry['passed'],
                     report_exactly_equal=not differences, report_differences=differences,
                     normal_gates={key: normal[key] for key in ('polygon_geometry_passed', 'polygon_geometry_max_abs', 'corner_newell_api_passed', 'corner_newell_api_max_abs', 'unit_length_error_max', 'flat', 'three_corners_equal', 'outward', 'comparison_limit', 'original_corner_geometry_passed', 'original_corner_geometry_max_abs', 'original_corner_geometry_max_angle_degrees')},
                     original_corner_faces_over_limit=normal['original_corner_geometry_faces_over_limit']))
    return raw, geometry

check(sha(OUT/'build-raw.json') == native['raw_sha256'], 'Baseline raw SHA')
check(sha(OUT/'build-exercise.json') == native['exercise_sha256'], 'Complete exercise SHA')
g.validate_candidate(c)
baseline, baseline_geometry = capture(OUT/'build-raw.json', native['validation'], wanted_state(), complete=True)
specs = [(r, 'value', r) for r in c['controls']] + [(r, p['id'], p) for r in c['controls'] for p in r.get('secondary_parameters', [])]
check(len(probes) == len(specs)+1 == 9, 'Eight prescribed control/secondary probes plus manual')
geometry_differences = []
for probe, (control, field, spec) in zip(probes[:-1], specs):
    check(probe['id'] == control['id'] and probe['field'] == field and probe['value'] == spec['exercise_value'] and probe['exact_identity_restored'] is True, 'Prescribed probe identity')
    states = {}
    for kind in ('moved', 'restored'):
        path = Path(probe[kind+'_path'])
        check(path.resolve().parent == OUT and sha(path) == probe[kind+'_sha256'], 'Control evidence boundary/SHA')
        state = wanted_state(control['id'], field, spec['exercise_value']) if kind == 'moved' else wanted_state()
        states[kind], geometry = capture(path, probe[kind+'_validation'], state)
        if kind == 'moved':
            geometry_differences += [dict(file=path.name, **d) for d in diffs(probe['geometry'], geometry)]
    check(states['moved']['mesh']['vertices'] != base['mesh']['vertices'], 'Actual control response')
    check(s.identity(states['restored']) == s.identity(base), 'Exact whole-raw numeric restoration')

probe, spec = probes[-1], c['manual_edit_probe']
check(probe['id'] == 'manual_edit' and probe['vertex_index'] == spec['vertex_index'] and probe['delta_local'] == spec['delta_local'] and probe['exact_identity_restored'] is True, 'Prescribed manual probe')
manual_base = [row[:] for row in base['mesh']['vertices']]
i = spec['vertex_index']
manual_base[i] = [s.f32(x+d) for x, d in zip(manual_base[i], spec['delta_local'])]
manual = {}
for kind in ('manual', 'combined', 'manual_restored', 'restored'):
    path = Path(probe[kind+'_path'])
    check(path.resolve().parent == OUT and sha(path) == probe[kind+'_sha256'], 'Manual evidence boundary/SHA')
    state = wanted_state(c['controls'][0]['id'], 'value', c['controls'][0]['exercise_value']) if kind == 'combined' else wanted_state()
    manual[kind], geometry = capture(path, probe[kind+'_validation'], state, manual_base=None if kind == 'restored' else manual_base)
    if kind == 'manual':
        geometry_differences += [dict(file=path.name, **d) for d in diffs(probe['geometry'], geometry)]
check(s.identity(manual['manual_restored']) == s.identity(manual['manual']), 'Whole-raw manual offset preservation')
check(s.identity(manual['restored']) == s.identity(base), 'Whole-raw manual baseline restoration')
check(manual['combined']['mesh']['vertices'] != manual['manual']['mesh']['vertices'], 'Actual combined response')
check(len(rows) == 21, 'All 21 actual raw captures read')

wrapper = read(RUN/'wrapper-report.json')
supervisor = read(RUN/'supervisor-terminal.json')
external = read(RUN/'external-caller/external-process-result.json')
process = read(RUN/'build.process.json')
events = [json.loads(line) for line in (OUT/'build-events.jsonl').read_text().splitlines()]
check(wrapper['stages'] == [process] and process['returncode'] == 0 and process['native_exit_observed'] is True, 'One actual exited build process')
check(native['source_saved'] is True and native['passed'] is True and native['state'] == 'completed', 'Actual successful native build')
check(len([e for e in events if e['stage'] == 'save.begin']) == len([e for e in events if e['stage'] == 'save.complete']) == 1, 'One observed save')
check(not any(e['stage'].startswith('fresh_open') for e in events) and not list(OUT.glob('verify-*')) and not (RUN/'verify.process.json').exists(), 'Fresh-open was not started')
check(external['actual_exit_code'] == 1 and external['process_exit_observed'] is True and external['remaining_owned_pids'] == [], 'Actual failed launcher terminal and no remaining owned processes')
check(supervisor['worker_exit_observed'] is True and supervisor['worker_returncode'] == 1 and supervisor['all_owned_children_reaped'] is True, 'Actual worker exit/reaping')
check(sha(RUN/'supervisor-terminal.json') == external['supervisor_terminal_sha256'], 'External receipt SHA')
check(sha(RUN/'wrapper-report.json') == supervisor['wrapper_report_sha256'] == supervisor['terminal_sha256'] == sha(HERE/'source-terminal.json'), 'Original failed wrapper/terminal receipt identities')
check(wrapper['passed'] is False and supervisor['passed'] is False and external['source_chain_verified'] is False, 'Never relabel failed source chain')
check(native['source_sha256'] == wrapper['source_sha256'] == sha(g.SOURCE) and native['source_bytes'] == wrapper['source_bytes'] == g.SOURCE.stat().st_size == 324985, 'Saved source byte identity')
before, after = read(RUN/'protected-before.json'), read(RUN/'protected-after.json')
check(before == after and len(before) == 14370, 'All original stage-protected file hashes identical')
inputs = hash_check(read(RUN/'input-sha256.json'))
old = hash_check(read(HERE/'OLD_SOURCE_PROTECTION.json')['files'])
protected_now = hash_check(after)
check(inputs['all_match'] and old['all_match'], 'Pinned runtime and original-source hashes still match')
for name, data in expected.items():
    check((OUT/'embedded-text-inputs'/name).read_bytes() == data, 'Embedded text input exact bytes')
check(all(sha(path) == digest for path, digest in before_bytes.items()), 'Existing outputs/source unchanged during this read-only replay')
differences = [dict(file=row['file'], **d) for row in rows for d in row['report_differences']]
allowed = {'/normals/geometric_direction_dot_min', '/normals/original_corner_geometry_max_angle_degrees'}
result = dict(scope='Read-only independent failure diagnosis; no replacement acceptance',
              source_chain_still_failed=True, fresh_open_started=False, fresh_open_passed=False,
              replay_complete=True, raw_captures=len(rows), control_probes=7, secondary_probes=1, manual_probe=True,
              all_actual_geometry_and_api_diagnostic_gates_replayed=True,
              exact_whole_raw_numeric_identity_restored=True,
              report_difference_count=len(differences), differing_report_count=sum(not row['report_exactly_equal'] for row in rows),
              observed_difference_paths=sorted({d['path'] for d in differences}),
              only_two_derived_normal_statistics_differ=all(d['path'] in allowed for d in differences),
              maximum_report_difference_ulps=max((d.get('ulps', 0) for d in differences), default=0),
              recorded_exercise_geometry_differences=geometry_differences,
              actual_build_process=process, actual_external_exit={k: external[k] for k in ('actual_exit_code', 'process_exit_observed', 'wall_seconds', 'remaining_owned_pids')},
              all_owned_children_reaped=supervisor['all_owned_children_reaped'], observed_save_count=1,
              saved_source=dict(path=str(g.SOURCE.relative_to(ROOT)), bytes=g.SOURCE.stat().st_size, sha256=sha(g.SOURCE)),
              baseline_geometry=baseline_geometry, raw_results=rows,
              original_stage_protection=dict(count=len(before), before_equals_after=before==after),
              current_protected_files=protected_now, current_frozen_inputs=inputs, current_old_source_protection=old,
              current_old_blends=[dict(path=path, sha256=digest, current_matches=sha(path)==digest) for path, digest in after.items() if '/revision-l/' in path and path.endswith('.blend')],
              preserved_outputs_and_source_unchanged_during_replay=True,
              caveats=['Exact whole-report equality still fails under the unchanged wrapper.',
                       'Derived statistic discrepancy observed; precise runtime/library cause not established.',
                       'Old corner-to-geometric-normal criterion remains failed; API consistency is separate.',
                       'Source save evidence and hash do not establish an independently reopened source.',
                       'All original 3e-5 and other geometry/protection gates remain unchanged.'])
print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
