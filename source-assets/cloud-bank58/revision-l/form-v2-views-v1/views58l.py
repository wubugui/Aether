"""Thin four-view binding for the already saved/recovered form-v2. No engine on import."""
from __future__ import annotations
import os, sys
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'form-v2-recovery-v1'))
import recovery58l as recovery
ROOT, FORM = recovery.ROOT, recovery.FORM
original, g, native, s, support, deadline = recovery.original, recovery.g, recovery.native, recovery.s, recovery.support, recovery.deadline
require, sha, read = recovery.require, recovery.sha, recovery.read
runtime, install_pidfd_bridge, require_source, verify_pins = recovery.runtime, recovery.install_pidfd_bridge, recovery.require_source, recovery.verify_pins
PYTHON, PYTHON_SHA, SOURCE_SHA, SOURCE_BYTES = recovery.PYTHON, recovery.PYTHON_SHA, recovery.SOURCE_SHA, recovery.SOURCE_BYTES
VERSION, STAGE = 'cloudbank58l-form-v2-views-v1', 'views'
TOTAL, CAPS = 120, {'render': 27}
VIEWS = ('01-original61-front', '02-k-trial-front', '03-k-fixed-side-back', '04-k-fixed-near')
ATTEMPT, TERMINAL, OBSERVATION = [HERE / ('views-' + x + '.json') for x in ('attempt', 'terminal', 'launch-observation')]

def predecessor():
    return read(HERE / 'RENDER_BINDINGS.json')['combined_predecessor']

def require_new_admission(stage, *, check_prior=True):
    require(stage == STAGE, 'Only recovered-source views; build/save/source/verify/export refused')
    for suffix in ('attempt', 'terminal', 'launch-observation', 'launch-validation'):
        p = HERE / ('views-' + suffix + '.json')
        require(not p.exists() and not p.is_symlink(), 'New views already attempted; preserve all one-shot evidence')
    require_source()
    pins = verify_pins(HERE / 'FINAL_SHA256.json')
    for p in HERE.parent.rglob('*-attempt.json'):
        require(not p.is_symlink() and p.is_file() and str(p) in pins and sha(p) == pins[str(p)],
                'Unknown or changed earlier admission')
    if check_prior:
        actual = recovery.prior_recovery()
        require(actual == predecessor(), 'Real old-build plus actual fresh-only combination; original source remains failed')
    return predecessor()

def exclusions():
    # Source, all old admissions/failures and old images remain protected.
    return {TERMINAL, TERMINAL.with_suffix('.json.tmp')}

def native_command(out, admission, view):
    require(view in VIEWS, 'Exactly one original view')
    return [str(g.BLENDER), '--factory-startup', '--disable-autoexec', '-b', '-t', '2', '--python-exit-code', '1',
            '--python', str(HERE / 'render_saved58l.py'), '--', '--mode', 'render', '--out', str(out),
            '--admission', str(admission), '--view', view]

def require_scope(record):
    require(record['original_source_stage'] == 'failed' and record['acceptance_mode'] == s.DIAGNOSTIC_MODE
            and record['full_native_acceptance'] is False, 'Recovered diagnostic views never full-native or old-source success')
    require(all(record[k] is False for k in ('world_loaded', 'world_integration_allowed', 'contact_acceptance',
            'world_acceptance', 'global_GOAL', 'visual_acceptance', 'weather_acceptance')), 'No visual/world/GOAL acceptance')

def verify_admission(a, path, out, view):
    require(path.resolve() == ATTEMPT and not path.is_symlink(), 'Only new views admission')
    require(view in VIEWS and a['views'] == list(VIEWS), 'Original four output bindings')
    require(a['state'] == 'admitted_one_shot_not_complete' and a['stage'] == STAGE and a['runner_version'] == VERSION,
            'New independent render-only admission identity')
    require(a['wrapper_pid'] == os.getppid() and a['native_sha256'] == sha(HERE / 'render_saved58l.py')
            and a['runner_sha256'] == sha(HERE / 'run_views58l.py'), 'Actual owner and new executable adapter identities')
    require(a['source_native_sha256'] == sha(FORM / 'native58l.py') and a['source'] == str(g.SOURCE)
            and a['source_sha256'] == SOURCE_SHA and a['source_bytes'] == SOURCE_BYTES, 'Original saved-source executable/Text identity')
    require(Path(a['output']).resolve() == out.resolve() and out.resolve().parent == Path(a['run'])
            and Path(a['run']).resolve().parent == ROOT / 'cloud-evidence', 'Actual new output/run boundary')
    require(a['candidate_sha256'] == sha(g.CANDIDATE_PATH) and a['binding_sha256'] == sha(g.BINDING_PATH)
            and a['render_bindings_sha256'] == sha(HERE / 'RENDER_BINDINGS.json'), 'Unchanged original candidate/camera inputs')
    require(a['predecessor'] == predecessor() and a['original_source_stage'] == 'failed'
            and a['acceptance_mode'] == s.DIAGNOSTIC_MODE and a['full_native_acceptance'] is False,
            'Actual recovered source combination, never old prior_source')
    require(not (out / (view + '.png')).exists() and not (out / (view + '.png')).is_symlink(), 'Never overwrite a view')

def validate_image(out, view, terminal):
    path = out / (view + '.png')
    require(view in VIEWS and path.is_file() and not path.is_symlink(), 'Actual new PNG file')
    image = original.png_info(path)
    require(terminal['image_path'] == str(path) and image['sha256'] == terminal['image_sha256'],
            'Actual new original image bytes, never a substituted old image')
    return image

def validate_render(out, view, row, cpus, admission_sha, c, b, baseline):
    """Same original raw/render/restore/PNG exact checks, plus actual new adapter binding."""
    require(view in VIEWS and support.process_passed(row), 'One successful actual render process')
    label = 'render-' + view
    require(row['command'] == native_command(out, ATTEMPT, view) and row['cpu_affinity'] == cpus
            and len(cpus) == 2 and 0 < row['wall_timeout_seconds'] <= CAPS['render']
            and 0 <= row['wall_seconds'] <= row['wall_timeout_seconds'], 'Original bounded CPU2 actual Popen command')
    original.require_positive_pid(row['pid'])
    require(not support.error_lines([out.parent / (label + '.stdout.log'), out.parent / (label + '.stderr.log')]), 'No actual native error/leak log')
    terminal = read(out / (label + '-result.json')); raw = read(out / (label + '-raw.json'))
    require(terminal['passed'] is True and terminal['state'] == 'completed' and terminal['version'] == g.VERSION
            and terminal['mode'] == 'render' and terminal['view'] == view and terminal['pid'] == row['pid'] == raw['pid'], 'Actual render terminal and PID')
    require_scope(terminal)
    require(terminal['views_version'] == VERSION and terminal['views_stage'] == STAGE and terminal['admission_sha256'] == admission_sha
            and terminal['adapter_sha256'] == sha(HERE / 'render_saved58l.py')
            and terminal['source_native_sha256'] == sha(FORM / 'native58l.py'), 'New adapter versus original embedded source identities')
    require(raw['cpu_affinity'] == cpus and terminal['raw_path'] == str(out / (label + '-raw.json'))
            and terminal['raw_sha256'] == sha(out / (label + '-raw.json')), 'Original baseline bytes')
    require(terminal['validation'] == g.validate_native_raw(raw, c, b), 'Full original baseline validation exactly equal')
    require(Path(raw['opened_filepath']).resolve() == g.SOURCE and s.identity(raw) == s.identity(baseline), 'Actual recovered source baseline identity')
    require(terminal['source_sha256'] == SOURCE_SHA and terminal['source_bytes'] == SOURCE_BYTES
            and terminal['source_saved'] is False and terminal['images'] == 1 and terminal['exact_identity_restored'] is True
            and terminal['diagnostic_acceptance'] is True, 'Exactly one no-save diagnostic image')
    image = validate_image(out, view, terminal)
    rendered = read(out / (label + '-rendered-raw.json'))
    require(terminal['rendered_raw_sha256'] == sha(out / (label + '-rendered-raw.json')) and rendered['pid'] == raw['pid'], 'Actual rendered RNA/PID')
    expected_settings = dict(raw['settings'], active_camera=s.CAMERA_PREFIX + view, render_filepath=str(out / (view + '.png')))
    require(rendered['settings'] == expected_settings and all(img['type'] == 'RENDER_RESULT' and img['source'] == 'VIEWER' for img in rendered['images']), 'Actual original active camera/filepath and native render result')
    require({k:v for k,v in s.identity(rendered).items() if k not in ('settings', 'images')}
            == {k:v for k,v in s.identity(raw).items() if k not in ('settings', 'images')}, 'Actual geometry/material/lighting/camera data unchanged during render')
    require(terminal['rendered_normals'] == s.validate_normals(rendered['mesh']), 'Original full rendered normals report exactly equal')
    restored = read(out / (label + '-restored-raw.json'))
    require(terminal['restored_validation'] == s.validate_capture(restored, c, b, s.expected_texts(FORM, c, b)), 'Full original restore oracle and source Text bytes')
    require(terminal['restored_raw_sha256'] == sha(out / (label + '-restored-raw.json')) and restored['pid'] == raw['pid']
            and s.identity(restored) == s.identity(raw), 'Complete original numeric scene identity restored')
    require_source()
    return dict(view=view, **image), terminal['validation']['normals']

def prior_views():
    runtime(); require_source(); verify_pins(HERE / 'FINAL_SHA256.json')
    require(recovery.prior_recovery() == predecessor(), 'Actual completed recovery prerequisite remains true')
    a, worker, observed = read(ATTEMPT), read(TERMINAL), read(OBSERVATION)
    run = Path(worker['run']); out = run / 'outputs'
    require(run.is_absolute() and run == run.resolve() and run.parent == ROOT / 'cloud-evidence'
            and run.name.startswith(VERSION + '-views-') and not run.is_symlink(), 'Actual new views run boundary')
    receipt = read(run / 'supervisor-terminal.json')
    require(TERMINAL.read_bytes() == (run / 'wrapper-report.json').read_bytes(), 'Actual worker terminal bytes')
    require(all(x['stage'] == STAGE and x['runner_version'] == VERSION and x['run'] == str(run)
                and x['source'] == str(g.SOURCE) and x['runner_sha256'] == sha(HERE / 'run_views58l.py')
                and x['predecessor'] == predecessor() for x in (a, worker, receipt)), 'One actual new views chain')
    require(a['state'] == 'admitted_one_shot_not_complete' and a['output'] == str(out) and a['views'] == list(VIEWS)
            and a['native_sha256'] == sha(HERE / 'render_saved58l.py') and a['source_native_sha256'] == sha(FORM / 'native58l.py')
            and a['candidate_sha256'] == sha(g.CANDIDATE_PATH) and a['binding_sha256'] == sha(g.BINDING_PATH)
            and a['render_bindings_sha256'] == sha(HERE / 'RENDER_BINDINGS.json'), 'Immutable actual new admission')
    require(receipt['limit_seconds'] == TOTAL and deadline.accepted(receipt), 'Actual original wait4 bounded completion')
    require(receipt['terminal_sha256'] == sha(TERMINAL) and receipt['wrapper_report_sha256'] == sha(run / 'wrapper-report.json')
            and observed['supervisor_terminal_sha256'] == sha(run / 'supervisor-terminal.json'), 'Full actual terminal SHA chain')
    require(type(observed['actual_exit_code']) is int and observed['actual_exit_code'] == 0 and observed['process_exit_observed'] is True
            and 0 < observed['wall_seconds'] < TOTAL and not observed['timeout'] and observed['remaining_owned_pids'] == []
            and not any(observed.get(k) for k in ('caller_error', 'cleanup_error', 'orphan_or_live_owned_detected')), 'Actual full launcher Popen/wait success')
    require(observed['command'] == [str(PYTHON), '-B', str(HERE / 'run_views58l.py'), '--run-approved', STAGE]
            and observed['runtime']['python_sha256'] == PYTHON_SHA, 'Official Python 3.11 actual external observer')
    require(a['wrapper_pid'] == worker['worker_pid'] == receipt['worker_pid'] and a['supervisor_pid'] == worker['supervisor_pid']
            == receipt['supervisor_pid'] == observed['supervisor_pid'] and receipt['worker_pid'] != receipt['supervisor_pid'], 'Actual owner/PID chain')
    require(worker['state'] == 'awaiting_external_process_terminal' and worker['passed'] is False and worker['prepared_passed'] is True
            and worker['intended_worker_exit_code'] == 0 and worker['completion_authority'] == str(run / 'supervisor-terminal.json'), 'Worker preparation is not completion')
    for x in (worker, receipt):
        require(x['original_source_stage'] == 'failed' and x['acceptance_mode'] == s.DIAGNOSTIC_MODE and x['full_native_acceptance'] is False
                and x['source_sha256'] == SOURCE_SHA and x['source_bytes'] == SOURCE_BYTES and x['admission_sha256'] == sha(ATTEMPT), 'Limited recovered-source scope')
    require_scope(worker)
    require(receipt['diagnostic_acceptance'] is True and worker['diagnostic_acceptance'] is False and worker['diagnostic_prepared_passed'] is True, 'External completion authority only')
    require(worker['limits'] == dict(total_wall_seconds=TOTAL, cpu_threads=2, native_caps=CAPS, max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB), 'Unchanged render limits')
    require(all(worker[k] is True for k in ('frozen_inputs_unchanged', 'protected_originals_unchanged', 'earlier_outputs_unchanged', 'saved_source_unchanged', 'source_diagnostic_only'))
            and not worker['changed_inputs'] and not worker['input_errors'], 'Full existing evidence preservation')
    before, after = read(run / 'protected-before.json'), read(run / 'protected-after.json')
    require(before == after and before[str(g.SOURCE)] == SOURCE_SHA, 'Source included in complete repository protection')
    actual = {str(p):sha(p) for p in out.rglob('*') if p.is_file()}
    require(all(not p.is_symlink() for p in out.rglob('*')) and actual == worker['views_output_sha256'], 'All actual new output bytes sealed')
    require(len(worker['stages']) == 4, 'Exactly four independent render children')
    c, b = read(g.CANDIDATE_PATH), read(g.BINDING_PATH); baseline = read(recovery.OLD_RUN / 'outputs/build-raw.json')
    images, normals, pids = [], [], []
    for view, row in zip(VIEWS, worker['stages']):
        require(row == read(run / ('render-' + view + '.process.json')) and row['pid'] not in (receipt['worker_pid'], receipt['supervisor_pid']), 'Actual separate registered native process')
        im, normal = validate_render(out, view, row, receipt['cpu_affinity'], sha(ATTEMPT), c, b, baseline)
        images.append(im); normals.append(dict(stage='render-' + view, **normal)); pids.append(row['pid'])
    require(len(set(pids)) == 4 and worker['images'] == images and worker['normal_validation_by_stage'] == normals, 'Four actual image/process/normal identities')
    require({p.name for p in out.glob('*.png')} == {v + '.png' for v in VIEWS}, 'Only four fresh output files')
    require_source()
    return dict(existing_saved_source_fresh_open_verified=True, views_chain_verified=True, original_source_stage='failed',
                source_sha256=SOURCE_SHA, source_bytes=SOURCE_BYTES, images=images, four_outputs_three_directions=True,
                acceptance_mode=s.DIAGNOSTIC_MODE, full_native_acceptance=False, visual_acceptance=False, world_acceptance=False, global_GOAL=False)
