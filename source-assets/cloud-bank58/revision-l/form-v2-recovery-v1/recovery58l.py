"""Narrow saved-source recovery contract. Imports are inert; no engine launch."""
from __future__ import annotations
import ctypes, hashlib, json, os, signal, sys
from pathlib import Path
from types import SimpleNamespace
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FORM = HERE.parent / 'form-v2'
OLD_RUN = ROOT / 'cloud-evidence/cloudbank58l-form-v2-source-20261002T203132Z-gplbz9_7'
VERSION = 'cloudbank58l-form-v2-recovery-v1'
STAGE = 'saved-source-fresh-open'
SOURCE_SHA = '33cc763abc893cce0de214ae3b4df19b8b7e3bbde6d268432b8fd3847e61cc4a'
SOURCE_BYTES = 324985
OLD_ADMISSION_SHA = '8216396cd70064b29057ed32fcd8c8f61eecaf1ccab4a949bc065c7ccb3d2e87'
OLD_TERMINAL_SHA = 'c4856a8ffeaf5b28280beab2316f32e5b02f52720fcfed39a546d3ab9b7e7531'
PYTHON = ROOT.parent / 'tools-feiting/blender-4.5.14-linux-x64/4.5/python/bin/python3.11'
PYTHON_SHA = '60b08089c60cbe81827b135c8fd9e206ba2ee6bf54aa1dbd0d6f56ac2d5914f6'
PYTHON_VERSION = '3.11.15 (main, Apr 25 2025, 12:39:20) [GCC 11.2.1 20220127 (Red Hat 11.2.1-9)]'
sys.path.insert(0, str(FORM))
import run58l_form_v2 as original
import geometry58l as g
import native58l as native
s = original.native_support
support = original.support
deadline = original.deadline58l_v3
require = s.require
sha = support.sha
read = support.strict_json
TOTAL = 120
CAPS = {'verify': 30}
ATTEMPT = HERE / (STAGE + '-attempt.json')
TERMINAL = HERE / (STAGE + '-terminal.json')
OBSERVATION = HERE / (STAGE + '-launch-observation.json')


def runtime(native_process=False):
    """No rounding/tolerance branch. Native and outside validation use 3.11.15."""
    import numpy
    require(sys.version == PYTHON_VERSION, 'Exact official bundled Python 3.11.15 runtime')
    require(PYTHON.is_file() and not PYTHON.is_symlink() and sha(PYTHON) == PYTHON_SHA,
            'Pinned official bundled Python executable')
    if not native_process:
        require(Path(sys.executable).resolve() == PYTHON.resolve(), 'Wrapper and observer use pinned Python')
    require(numpy.__version__ == '1.26.4' and Path(numpy.__file__).resolve().is_relative_to(PYTHON.parents[1]),
            'Official bundled NumPy dependency')
    for module, path in ((original, FORM / 'run58l_form_v2.py'), (g, FORM / 'geometry58l.py'),
                         (native, FORM / 'native58l.py'), (s, FORM / 'native_support58l.py')):
        require(Path(module.__file__).resolve() == path, 'Unmodified original module origin')
    return dict(executable=sys.executable, version=sys.version, numpy_version=numpy.__version__,
                python_sha256=sha(PYTHON), numpy_file=numpy.__file__)


def install_pidfd_bridge():
    """Only supply absent os.pidfd_open to the unchanged supervisor module.

    This host's libc exports pidfd_open. No syscall numbers, PID-signaling fallback,
    broad monkeypatch, process discovery change or supervisor source change.
    """
    if hasattr(deadline.os, 'pidfd_open'):
        return
    libc = ctypes.CDLL(None, use_errno=True)
    call = libc.pidfd_open
    call.argtypes = (ctypes.c_int, ctypes.c_uint)
    call.restype = ctypes.c_int

    def pidfd_open(pid, flags=0):
        require(type(pid) is int and 0 < pid <= 2147483647 and type(flags) is int and flags == 0,
                'Only positive owned PIDs and original zero pidfd flags')
        fd = call(pid, flags)
        if fd < 0:
            number = ctypes.get_errno()
            raise OSError(number, os.strerror(number))
        try:
            os.set_inheritable(fd, False)
        except BaseException:
            os.close(fd)
            raise
        return fd

    deadline.os = SimpleNamespace(**dict(vars(os), pidfd_open=pidfd_open))


def require_source(path=None):
    path = g.SOURCE if path is None else Path(path)
    require(path.is_file() and not path.is_symlink(), 'Existing saved source required; no rebuild or fallback')
    require(path.stat().st_size == SOURCE_BYTES and sha(path) == SOURCE_SHA,
            'Exact existing saved-source SHA/size required')
    return SOURCE_SHA


def verify_pins(path):
    result = {}
    for rel, row in read(path)['files'].items():
        p = ROOT / rel
        require(not p.is_symlink() and p.is_file() and p.resolve().is_relative_to(ROOT), 'Frozen real project file ' + rel)
        require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'Exact frozen bytes ' + rel)
        result[str(p)] = row['sha256']
    result[str(path)] = sha(path)
    return result


def saved_predecessor(*, check_pins=True):
    """The original SOURCE stage is failed, while its sole native BUILD succeeded."""
    require_source()
    if check_pins:
        verify_pins(HERE / 'PREDECESSOR_SHA256.json')
    a = read(FORM / 'source-attempt.json')
    old = read(FORM / 'source-terminal.json')
    receipt = read(OLD_RUN / 'supervisor-terminal.json')
    observation = read(FORM / 'source-launch-observation.json')
    build = read(OLD_RUN / 'outputs/build-result.json')
    process = read(OLD_RUN / 'build.process.json')
    raw = read(OLD_RUN / 'outputs/build-raw.json')
    require(sha(FORM / 'source-attempt.json') == OLD_ADMISSION_SHA and sha(FORM / 'source-terminal.json') == OLD_TERMINAL_SHA,
            'Exact failed original admission and terminal retained')
    require((FORM / 'source-terminal.json').read_bytes() == (OLD_RUN / 'wrapper-report.json').read_bytes(), 'Original failed terminal bytes')
    require(all(r['stage'] == 'source' and r['runner_version'] == original.VERSION and r['run'] == str(OLD_RUN)
                and r['source'] == str(g.SOURCE) for r in (a, old, receipt)), 'Exact original source chain')
    require(old['state'] == 'failed' and old['passed'] is False and old['prepared_passed'] is False
            and old['intended_worker_exit_code'] == 1 and old['saved_source_unchanged'] is False
            and old['source_output_sha256'] == {} and 'Independent complete actual raw validation' in old['error'],
            'Preserved specific report-equality failure, never old source success')
    require(receipt['passed'] is False and receipt['state'] == 'failed' and receipt['worker_exit_observed'] is True
            and receipt['worker_returncode'] == 1 and receipt['all_owned_children_reaped'] is True
            and receipt['source_sha256'] is None and receipt['source_bytes'] is None, 'Complete original failed supervisor terminal')
    require(receipt['terminal_sha256'] == receipt['wrapper_report_sha256'] == OLD_TERMINAL_SHA
            and observation['supervisor_terminal_sha256'] == sha(OLD_RUN / 'supervisor-terminal.json'), 'Original failure sealed bytes')
    require(observation['actual_exit_code'] == 1 and observation['process_exit_observed'] is True
            and 0 < observation['wall_seconds'] < TOTAL and observation['remaining_owned_pids'] == [], 'Original actual whole-launcher failure')
    require(old['stages'] == [process] and support.process_passed(process)
            and process['command'] == original.native_command(g, 'build', OLD_RUN / 'outputs', FORM / 'source-attempt.json'),
            'Exactly one original successful real build, no prior fresh-open')
    for pid in (process['pid'], a['wrapper_pid'], a['supervisor_pid']):
        original.require_positive_pid(pid)
    require(process['pid'] == build['pid'] == raw['pid'] and a['wrapper_pid'] == old['worker_pid'] == receipt['worker_pid']
            and a['supervisor_pid'] == old['supervisor_pid'] == receipt['supervisor_pid'] == observation['supervisor_pid'], 'Original actual PID chain')
    require(build['mode'] == 'build' and build['passed'] is True and build['state'] == 'completed'
            and build['source_saved'] is True and build['images'] == 0 and build['controls_exercised'] == 7
            and build['secondary_exercised'] == 1 and build['manual_edit_exercised'] is True
            and build['exact_identity_restored'] is True, 'Original single-save build and complete edit exercise')
    require(build['source_sha256'] == old['source_sha256'] == SOURCE_SHA and build['source_bytes'] == old['source_bytes'] == SOURCE_BYTES
            and build['raw_sha256'] == sha(OLD_RUN / 'outputs/build-raw.json')
            and build['exercise_sha256'] == sha(OLD_RUN / 'outputs/build-exercise.json'), 'Original saved source and raw/exercise bytes')
    require(raw['opened_filepath'] == '' and not list((OLD_RUN / 'outputs').glob('verify*')),
            'No old fresh-open result exists')
    require(build['acceptance_mode'] == s.DIAGNOSTIC_MODE and build['full_native_acceptance'] is False
            and build['validation']['normals']['original_corner_geometry_passed'] is False,
            'Old and new normal acceptance scopes remain separate')
    return dict(original_source_stage='failed', original_admission_sha256=OLD_ADMISSION_SHA,
                original_terminal_sha256=OLD_TERMINAL_SHA, original_build_result_sha256=sha(OLD_RUN / 'outputs/build-result.json'),
                original_build_raw_sha256=sha(OLD_RUN / 'outputs/build-raw.json'), source_sha256=SOURCE_SHA,
                source_bytes=SOURCE_BYTES, original_build_pid=process['pid'])


def require_new_admission(stage):
    require(stage == STAGE, 'Only existing saved-source fresh-open; build/source/views refused')
    for name in (STAGE + '-attempt.json', STAGE + '-terminal.json', STAGE + '-launch-observation.json', STAGE + '-launch-validation.json'):
        p = HERE / name
        require(not p.exists() and not p.is_symlink(), 'Recovery already attempted; preserve one-shot evidence')
    # Every consumed historical admission is frozen, including old failed source.
    known = read(HERE / 'PREDECESSOR_SHA256.json')['files']
    for p in HERE.parent.rglob('*-attempt.json'):
        require(not p.is_symlink() and p.is_file() and str(p.relative_to(ROOT)) in known
                and sha(p) == known[str(p.relative_to(ROOT))]['sha256'],
                'Unknown or changed historical attempt; stop')
    return saved_predecessor()


def exclusions():
    # Existing .blend is intentionally NEVER excluded, regardless of stage naming.
    return {TERMINAL, TERMINAL.with_suffix('.json.tmp')}


def native_command(out, admission):
    return [str(g.BLENDER), '--factory-startup', '--disable-autoexec', '-b', '-t', '2', '--python-exit-code', '1',
            '--python', str(HERE / 'verify_saved58l.py'), '--', '--mode', 'verify', '--out', str(out), '--admission', str(admission)]


def verify_admission(a, path, out):
    require(path.resolve() == ATTEMPT and not path.is_symlink(), 'Only new recovery admission path')
    require(a['state'] == 'admitted_one_shot_not_complete' and a['stage'] == STAGE and a['runner_version'] == VERSION,
            'Actual saved-source fresh-only admission identity')
    require(a['wrapper_pid'] == os.getppid() and a['native_sha256'] == sha(HERE / 'verify_saved58l.py'), 'Actual native owner and code')
    require(a['source'] == str(g.SOURCE) and a['source_sha256'] == SOURCE_SHA and a['source_bytes'] == SOURCE_BYTES
            and Path(a['output']).resolve() == out.resolve(), 'Admitted existing source/output identity')
    require(a['candidate_sha256'] == sha(g.CANDIDATE_PATH) and a['binding_sha256'] == sha(g.BINDING_PATH), 'Original form inputs')
    require(a['predecessor'] == saved_predecessor(check_pins=False) and a['acceptance_mode'] == s.DIAGNOSTIC_MODE
            and a['full_native_acceptance'] is False, 'Exact failed-source/successful-build predecessor')


def prior_recovery():
    """Future views bind old successful build PLUS new fresh-only actual completion.

    This never calls or rewrites original.prior_source, which must still reject the
    failed original whole source stage. No render is admitted by this function.
    """
    runtime()
    predecessor = saved_predecessor()
    verify_pins(HERE / 'FINAL_SHA256.json')
    a, worker, observed = read(ATTEMPT), read(TERMINAL), read(OBSERVATION)
    run = Path(worker['run'])
    require(run.is_absolute() and run == run.resolve() and run.parent == ROOT / 'cloud-evidence'
            and run.name.startswith(VERSION + '-' + STAGE + '-') and not run.is_symlink(), 'Actual recovery run boundary')
    out = run / 'outputs'
    receipt_path, wrapper_path = run / 'supervisor-terminal.json', run / 'wrapper-report.json'
    receipt = read(receipt_path)
    require(TERMINAL.read_bytes() == wrapper_path.read_bytes(), 'Actual recovery worker terminal bytes')
    require(all(x['stage'] == STAGE and x['runner_version'] == VERSION and x['run'] == str(run)
                and x['source'] == str(g.SOURCE) and x['runner_sha256'] == sha(HERE / 'run_saved58l.py')
                and x['predecessor'] == predecessor for x in (a, worker, receipt)), 'Recovery identity and exact failed original predecessor')
    require(a['state'] == 'admitted_one_shot_not_complete' and a['output'] == str(out)
            and a['native_sha256'] == sha(HERE / 'verify_saved58l.py')
            and a['candidate_sha256'] == sha(g.CANDIDATE_PATH) and a['binding_sha256'] == sha(g.BINDING_PATH), 'Actual fresh-only admission inputs')
    require(receipt['limit_seconds'] == TOTAL and deadline.accepted(receipt), 'Actual bounded wait4 completion')
    require(receipt['terminal_sha256'] == sha(TERMINAL) and receipt['wrapper_report_sha256'] == sha(wrapper_path)
            and observed['supervisor_terminal_sha256'] == sha(receipt_path), 'Full outer observed receipt/worker SHA chain')
    for pid in (a['wrapper_pid'], a['supervisor_pid'], worker['worker_pid'], receipt['worker_pid'], observed['supervisor_pid']):
        original.require_positive_pid(pid)
    require(a['wrapper_pid'] == worker['worker_pid'] == receipt['worker_pid']
            and a['supervisor_pid'] == worker['supervisor_pid'] == receipt['supervisor_pid'] == observed['supervisor_pid']
            and receipt['worker_pid'] != receipt['supervisor_pid'], 'Actual recovery owner/worker/outer PID chain')
    require(type(observed['actual_exit_code']) is int and observed['actual_exit_code'] == 0
            and observed['process_exit_observed'] is True and 0 < observed['wall_seconds'] < TOTAL
            and not observed['timeout'] and observed['remaining_owned_pids'] == []
            and not any(observed.get(k) for k in ('caller_error', 'cleanup_error', 'orphan_or_live_owned_detected')),
            'Actual whole launcher Popen/wait success within 120 seconds')
    require(observed['command'] == [str(PYTHON), '-B', str(HERE / 'run_saved58l.py'), '--run-approved', STAGE]
            and observed['runtime']['python_sha256'] == PYTHON_SHA, 'Pinned external caller and wrapper interpreter')
    require(worker['state'] == 'awaiting_external_process_terminal' and worker['prepared_passed'] is True
            and worker['passed'] is False and worker['intended_worker_exit_code'] == 0
            and worker['completion_authority'] == str(receipt_path), 'Worker preparation is not fabricated completion')
    for x in (worker, receipt):
        require(x['original_source_stage'] == 'failed' and x['acceptance_mode'] == s.DIAGNOSTIC_MODE
                and x['full_native_acceptance'] is False and x['source_sha256'] == SOURCE_SHA
                and x['source_bytes'] == SOURCE_BYTES and x['admission_sha256'] == sha(ATTEMPT), 'Exact source SHA and limited recovery scope')
    require(receipt['diagnostic_acceptance'] is True and worker['diagnostic_acceptance'] is False
            and worker['diagnostic_prepared_passed'] is True, 'External authority only')
    require(worker['limits'] == dict(total_wall_seconds=TOTAL, cpu_threads=2, native_caps=CAPS,
                                    max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB), 'Unchanged recovery limits')
    require(all(worker[k] is True for k in ('frozen_inputs_unchanged', 'protected_originals_unchanged',
            'earlier_outputs_unchanged', 'saved_source_unchanged', 'source_diagnostic_only'))
            and worker['images'] == [] and not worker['changed_inputs'] and not worker['input_errors'], 'Full recovery preservation evidence')
    require(all(worker[k] is False for k in ('world_loaded', 'world_modified', 'world_integration_allowed',
            'contact_acceptance', 'world_acceptance', 'global_GOAL', 'visual_acceptance', 'weather_acceptance')), 'No world/visual acceptance')
    before, after = read(run / 'protected-before.json'), read(run / 'protected-after.json')
    require(before == after and before[str(g.SOURCE)] == SOURCE_SHA, 'Existing saved source included in full before/after protection')
    actual_outputs = {str(p): sha(p) for p in out.rglob('*') if p.is_file()}
    require(all(not p.is_symlink() for p in out.rglob('*')) and actual_outputs == worker['recovery_output_sha256'], 'All fresh-only output bytes')
    require(len(worker['stages']) == 1, 'Exactly one fresh-open child; zero build children')
    row = worker['stages'][0]
    original.require_positive_pid(row['pid'])
    require(row == read(run / 'verify.process.json') and support.process_passed(row)
            and row['command'] == native_command(out, ATTEMPT) and row['cpu_affinity'] == receipt['cpu_affinity']
            and len(row['cpu_affinity']) == 2 and row['pid'] not in (receipt['worker_pid'], receipt['supervisor_pid'])
            and 0 < row['wall_timeout_seconds'] <= CAPS['verify'] and 0 <= row['wall_seconds'] <= row['wall_timeout_seconds'],
            'One actual bounded separately registered fresh-only process')
    terminal, raw = read(out / 'verify-result.json'), read(out / 'verify-raw.json')
    c, b = read(g.CANDIDATE_PATH), read(g.BINDING_PATH)
    require(terminal['passed'] is True and terminal['state'] == 'completed' and terminal['mode'] == 'verify'
            and terminal['view'] is None and terminal['version'] == g.VERSION and terminal['pid'] == raw['pid'] == row['pid']
            and raw['cpu_affinity'] == row['cpu_affinity'] and terminal['recovery_version'] == VERSION
            and terminal['recovery_stage'] == STAGE and terminal['original_source_stage'] == 'failed'
            and terminal['admission_sha256'] == sha(ATTEMPT), 'Actual completed verify-only native identity')
    require(terminal['source_saved'] is False and terminal['images'] == 0 and terminal['controls_exercised'] == 7
            and terminal['secondary_exercised'] == 1 and terminal['manual_edit_exercised'] is True
            and terminal['exact_identity_restored'] is True, 'In-memory original edit exercise, no save/render')
    require(terminal['raw_sha256'] == sha(out / 'verify-raw.json') and terminal['raw_path'] == str(out / 'verify-raw.json')
            and terminal['exercise_sha256'] == sha(out / 'verify-exercise.json')
            and terminal['source_sha256'] == SOURCE_SHA and terminal['source_bytes'] == SOURCE_BYTES, 'Native output/source exact bytes')
    require(terminal['validation'] == g.validate_native_raw(raw, c, b), 'Original full raw report exact equality')
    require(terminal['acceptance_mode'] == s.DIAGNOSTIC_MODE and terminal['diagnostic_acceptance'] is True
            and terminal['full_native_acceptance'] is False and all(terminal[k] is False for k in
            ('world_loaded', 'world_integration_allowed', 'contact_acceptance', 'world_acceptance', 'global_GOAL', 'visual_acceptance', 'weather_acceptance')), 'Only API diagnostic recovery accepted')
    require(Path(raw['opened_filepath']).resolve() == g.SOURCE and s.identity(raw) == s.identity(read(OLD_RUN / 'outputs/build-raw.json')),
            'Actual original saved-source fresh-open path and full baseline identity')
    require(worker['exercise'] == [original.validate_exercise(out, 'verify', c, b, g, raw)], 'Full original fresh-open exercise report equality')
    require(not support.error_lines([run / 'verify.stdout.log', run / 'verify.stderr.log']), 'No native error/leak log')
    require_source()
    return dict(predecessor=predecessor, recovery_admission_sha256=sha(ATTEMPT), recovery_terminal_sha256=sha(TERMINAL),
                recovery_supervisor_sha256=sha(receipt_path), recovery_observation_sha256=sha(OBSERVATION),
                existing_saved_source_fresh_open_verified=True, original_source_stage='failed',
                full_native_acceptance=False, visual_acceptance=False, world_acceptance=False, global_GOAL=False)
