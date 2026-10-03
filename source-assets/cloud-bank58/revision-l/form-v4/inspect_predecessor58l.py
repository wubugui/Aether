"""Read-only completed predecessor check after disclosed environment recovery.

Only four exact CPython3.12 derived-cache entries may be absent. Original
validators/files are never modified or patched. The original source validator
runs directly; the views body below differs only at its freeze-check call.
"""
from pathlib import Path
import hashlib, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CACHE_ROOT = 'source-assets/cloud-bank58/revision-l/source-v1/__pycache__/'
CACHE_EXEMPTIONS = {
    CACHE_ROOT + name + suffix: dict(bytes=size, sha256=sha)
    for name, size, sha in (
        ('native58l', 60334, '15829257bc56154dca88996451bad0c30ff040927bda06bf196ecccd9dbb1410'),
        ('native_support58l', 30952, 'aebc3398f801f747fe7d9a50c17eec12dfaf04461fe76d5224c5d676af2ac78b'))
    for suffix in ('.cpython-312.pyc', '.cpython-312.opt-1.pyc')
}
AUTHORITY_SOURCES = {
    'source-assets/cloud-bank58/revision-l/source-v1/native58l.py': dict(bytes=25743, sha256='a0d9059d2d94f14bd7890b6835674f45a2d8b6fc9a0d8d69ee3440376b1007ad'),
    'source-assets/cloud-bank58/revision-l/source-v1/native_support58l.py': dict(bytes=15961, sha256='e8cd215f0170453d9fd7c38b68641c0dfb8fa09f59b3eb4e91b1b1f627932ff1')
}

def require(ok, message):
    if not ok: raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path): return json.loads(Path(path).read_text())

def exact_file(root, rel, row):
    p = Path(root) / rel
    require(not Path(rel).is_absolute() and p.resolve().is_relative_to(Path(root).resolve())
            and not p.is_symlink() and p.is_file(), 'Frozen real project file ' + rel)
    require(p.stat().st_size == row['bytes'] and sha(p) == row['sha256'], 'Exact frozen bytes ' + rel)
    return p

def verify_restored_pins(path, *, root=ROOT):
    """Explicit four missing-cache exception, never a generic missing-file skip."""
    require(sys.dont_write_bytecode is True, 'Bytecode writes must stay disabled')
    rows = read(path)['files']; missing = []
    require(type(rows) is dict and rows, 'Nonempty original freeze')
    require(all(rows.get(rel) == row for rel, row in CACHE_EXEMPTIONS.items()),
            'Exactly the four authorized historical cache identities must be bound')
    for rel, row in AUTHORITY_SOURCES.items():
        require(rows.get(rel) == row, 'Exact authoritative source identity bound')
        exact_file(root, rel, row)
    for rel, row in rows.items():
        p = Path(root) / rel
        if rel in CACHE_EXEMPTIONS and not p.exists() and not p.is_symlink():
            missing.append(rel)
        else:
            exact_file(root, rel, row)
    return dict(freeze=str(Path(path).relative_to(root)), freeze_sha256=sha(path),
                original_entries=len(rows), verified_entries=len(rows)-len(missing),
                missing_derived_cache_entries=sorted(missing),
                allowed_cache_exemptions=CACHE_EXEMPTIONS, authority_sources=AUTHORITY_SOURCES,
                original_freeze_fully_restored=not missing, bytecode_writes_disabled=True)


def original_failures():
    import runtime58l
    with runtime58l.legacy() as (recovery, views):
        old = recovery.original.diagnostic58l.original_failures()
        verify_restored_pins(recovery.HERE / 'PREDECESSOR_SHA256.json')
        failed = recovery.saved_predecessor(check_pins=False)
        require(failed['original_source_stage'] == 'failed', 'Historical form-v2 source remains failed')
        return old + [recovery.OLD_ADMISSION_SHA]


def restored_views(views):
    # Local aliases of unchanged original functions; no mutation of their globals.
    runtime, require_source = views.runtime, views.require_source
    require, sha, read = views.require, views.sha, views.read
    HERE, ROOT, FORM, g = views.HERE, views.ROOT, views.FORM, views.g
    completed_source, predecessor = views.completed_source, views.predecessor
    ATTEMPT, TERMINAL, OBSERVATION = views.ATTEMPT, views.TERMINAL, views.OBSERVATION
    VERSION, STAGE, VIEWS = views.VERSION, views.STAGE, views.VIEWS
    SOURCE_RUN, SOURCE_SHA, SOURCE_BYTES = views.SOURCE_RUN, views.SOURCE_SHA, views.SOURCE_BYTES
    PYTHON, PYTHON_SHA = views.PYTHON, views.PYTHON_SHA
    TOTAL, CAPS, deadline = views.TOTAL, views.CAPS, views.deadline
    s, support = views.s, views.support
    require_scope, validate_render = views.require_scope, views.validate_render
    runtime(); require_source(); verify_restored_pins(HERE / 'FINAL_SHA256.json')
    require(completed_source() == predecessor(), 'Actual completed form-v3 prerequisite remains true')
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
                and x['source_sha256'] == SOURCE_SHA and x['source_bytes'] == SOURCE_BYTES and x['admission_sha256'] == sha(ATTEMPT), 'Limited saved-form-v3 scope')
    require_scope(worker)
    require(receipt['historical_form_v2_default_failure'] == s.HISTORICAL_FORM_V2_DEFAULT_FAILURE, 'Historical form-v2 23-face failure preserved')
    require(receipt['diagnostic_acceptance'] is True and worker['diagnostic_acceptance'] is False and worker['diagnostic_prepared_passed'] is True, 'External completion authority only')
    require(worker['limits'] == dict(total_wall_seconds=TOTAL, cpu_threads=2, native_caps=CAPS, max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB), 'Unchanged render limits')
    require(all(worker[k] is True for k in ('frozen_inputs_unchanged', 'protected_originals_unchanged', 'earlier_outputs_unchanged', 'saved_source_unchanged', 'source_diagnostic_only'))
            and not worker['changed_inputs'] and not worker['input_errors'], 'Full existing evidence preservation')
    before, after = read(run / 'protected-before.json'), read(run / 'protected-after.json')
    require(before == after and before[str(g.SOURCE)] == SOURCE_SHA, 'Source included in complete repository protection')
    actual = {str(p):sha(p) for p in out.rglob('*') if p.is_file()}
    require(all(not p.is_symlink() for p in out.rglob('*')) and actual == worker['views_output_sha256'], 'All actual new output bytes sealed')
    require(len(worker['stages']) == 4, 'Exactly four independent render children')
    c, b = read(g.CANDIDATE_PATH), read(g.BINDING_PATH); baseline = read(SOURCE_RUN / 'outputs/build-raw.json')
    images, normals, pids = [], [], []
    for view, row in zip(VIEWS, worker['stages']):
        require(row == read(run / ('render-' + view + '.process.json')) and row['pid'] not in (receipt['worker_pid'], receipt['supervisor_pid']), 'Actual separate registered native process')
        im, normal = validate_render(out, view, row, receipt['cpu_affinity'], sha(ATTEMPT), c, b, baseline)
        images.append(im); normals.append(dict(stage='render-' + view, **normal)); pids.append(row['pid'])
    require(len(set(pids)) == 4 and worker['images'] == images and worker['normal_validation_by_stage'] == normals, 'Four actual image/process/normal identities')
    require({p.name for p in out.glob('*.png')} == {v + '.png' for v in VIEWS}, 'Only four fresh output files')
    require_source()
    return dict(source_chain_verified=True, views_chain_verified=True, original_source_stage='failed',
                source_sha256=SOURCE_SHA, source_bytes=SOURCE_BYTES, images=images, four_outputs_three_directions=True,
                acceptance_mode=s.DIAGNOSTIC_MODE, full_native_acceptance=False, visual_acceptance=False, world_acceptance=False, global_GOAL=False)


def inspect_completed():
    import runtime58l
    failures = original_failures()
    with runtime58l.previous() as views:
        source_freeze = verify_restored_pins(views.FORM / 'FINAL_SHA256.json')
        views_freeze = verify_restored_pins(views.HERE / 'FINAL_SHA256.json')
        completed = restored_views(views)
        source = views.predecessor()  # Exact equality established in restored_views.
        require(source['source_chain_verified'] is True and completed['views_chain_verified'] is True,
                'Genuine completed form-v3 source and views')
        return dict(published_commit=runtime58l.PUBLISHED_PREDECESSOR,
                    original_source_stage='failed', original_source_stage_refers_to='form-v2',
                    completed_source=source, completed_views=completed, failure_admissions=failures,
                    environment_recovery=dict(published_commit=runtime58l.PUBLISHED_RECOVERY,
                                              source_freeze=source_freeze, views_freeze=views_freeze,
                                              historical_protected_directory_recreated=False))


if __name__ == '__main__':
    import runtime58l
    value = runtime58l.inspect_historical()
    destination = HERE / 'PREDECESSOR_RESULT.json'
    with destination.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False); stream.write('\n')
    print(json.dumps(dict(path=str(destination), source_chain_verified=value['completed_source']['source_chain_verified'],
                         views_chain_verified=value['completed_views']['views_chain_verified'],
                         original_source_stage=value['original_source_stage'],
                         source_freeze_entries=value['environment_recovery']['source_freeze']['verified_entries'],
                         views_freeze_entries=value['environment_recovery']['views_freeze']['verified_entries'])))
