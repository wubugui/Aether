#!/usr/bin/env python3
"""Default: pure checks only. Explicit reviewed admission: one bounded native read."""
import argparse, os, resource, signal, sys, tempfile, time, traceback
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import restore_contract62 as r
c, support = r.c, r.support
TOTAL_SECONDS, NATIVE_SECONDS, FINAL_RESERVE = 60, 30, 8


def native_command(root, source, output):
    return [str(c.BLENDER), '--factory-startup', '--disable-autoexec', '-b', '-t', '2',
            '--python-exit-code', '1', '--python', str(r.HERE / 'probe_restored62.py'), '--',
            '--restore-root', str(root), '--restored-source', str(source), '--out', str(output)]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--restore-root', type=Path)
    ap.add_argument('--restored-source', type=Path)
    ap.add_argument('--run-approved', action='store_true')
    args = ap.parse_args(argv)
    c.require(bool(args.restore_root) == bool(args.restored_source), 'Provide both explicit restored paths or neither')
    if not args.run_approved:
        r.preparation_inputs(require_local_freeze=(r.HERE / 'FINAL_SHA256.json').exists()); c.check_binding(c.read(c.BINDING_PATH))
        if args.restore_root:
            r.restore_identity(args.restore_root, args.restored_source)
        print('Pure checks passed; no native process, restoration, source save, rebuild or images. Local review/freeze and parent scheduling still required.')
        return 0
    c.require(args.restore_root is not None, 'Native admission requires an explicit existing restore root and source')
    # Never restore here. Parent first verifies remote storage and separately reconstructs.
    root, source = r.no_symlinks(args.restore_root), r.no_symlinks(args.restored_source)
    c.require(source == root / r.SOURCE_REL and not root.is_relative_to(c.ROOT) and
              not c.ROOT.is_relative_to(root), 'Explicit separate restored paths required')
    c.require((r.HERE / 'FINAL_SHA256.json').is_file(), 'Parent review and freeze required before admission')
    with (r.HERE / 'restore-read-attempt.json').open('x') as f:
        c.json.dump(dict(state='admitted_one_shot_not_complete', pid=os.getpid(),
                         restore_root=str(args.restore_root), restored_source=str(args.restored_source),
                         utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())), f)
        f.flush(); os.fsync(f.fileno())
    started = time.monotonic()
    run = Path(tempfile.mkdtemp(prefix='north-ridge62-restore-read-v1-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '-', dir=c.ROOT / 'cloud-evidence'))
    print(run, flush=True)
    report = dict(version=r.VERSION, state='preparing', passed=False, run=str(run),
                  restore_root=str(args.restore_root), restored_source=str(args.restored_source),
                  limits=dict(total_wall_seconds=TOTAL_SECONDS, native_wall_seconds=NATIVE_SECONDS,
                              cpu_threads=2, max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),
                  stages=[], source_saved=False, rebuild_performed=False, images=0,
                  godot_started=False, world_loaded=False, world_modified=False,
                  world_integration_allowed=False, visual_acceptance=False)
    pins, before, restored_before, handlers, outputs = {}, {}, {}, {}, {}
    def stop(number, frame):
        raise InterruptedError('Wrapper stop signal ' + str(number))
    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            handlers[sig] = signal.signal(sig, stop)
        signal.setitimer(signal.ITIMER_REAL, TOTAL_SECONDS)
        cpus = sorted(os.sched_getaffinity(0))[:2]
        c.require(len(cpus) == 2, 'CPU2 available'); os.sched_setaffinity(0, cpus)
        pins = r.preparation_inputs(require_local_freeze=True)
        c.require(c.sha(c.BLENDER) == c.BLENDER_SHA, 'Pinned official Blender executable')
        before, restored_before = r.protected_identity(), r.restore_identity(args.restore_root, args.restored_source)
        support.atomic_json(run / 'protected-before.json', before)
        support.atomic_json(run / 'restored-before.json', restored_before)
        support.atomic_json(run / 'input-sha256.json', pins)
        output = run / 'outputs'; output.mkdir()
        env = os.environ.copy(); env.pop('PYTHONOPTIMIZE', None)
        env.update(OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2',
                   PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
        for key, name in [('XDG_CONFIG_HOME', 'config'), ('XDG_CACHE_HOME', 'cache'),
                          ('XDG_DATA_HOME', 'data'), ('BLENDER_USER_CONFIG', 'blender-config')]:
            path = run / name; path.mkdir(); env[key] = str(path)
        remaining = TOTAL_SECONDS - (time.monotonic() - started) - FINAL_RESERVE
        c.require(remaining > 0, 'Total wall budget exhausted before native read')
        report['state'] = 'running'; support.atomic_json(run / 'wrapper-report.json', report)
        # Same audited actual-PID/wait4/RSS/kill-reap helper as recovery-v2; no replacement framework.
        row = support.run_child(native_command(args.restore_root, args.restored_source, output),
                                run, env, run, min(NATIVE_SECONDS, remaining), 'restore-read')
        report['stages'].append(row); support.atomic_json(run / 'wrapper-report.json', report)
        c.require(support.process_passed(row), 'Native read child failed')
        c.require(not support.error_lines([run / 'restore-read.stdout.log', run / 'restore-read.stderr.log']), 'Native error/leak log')
        terminal = support.strict_json(output / 'restore-read-result.json')
        rawpath = output / 'restore-read-raw.json'; raw = c.read(rawpath)
        c.require(terminal['version'] == r.VERSION and terminal['recovery_version'] == c.RECOVERY_VERSION and
                  terminal['mode'] == 'restore-read' and terminal['passed'] is True and terminal['state'] == 'completed', 'Actual completed native report')
        c.require(terminal['pid'] == raw['pid'] == row['pid'], 'Actual native PID identity')
        c.require(raw['cpu_affinity'] == row['cpu_affinity'] == cpus, 'Actual CPU2 identity')
        c.require(terminal['raw_sha256'] == c.sha(rawpath), 'Raw persisted before validation SHA binding')
        c.require(terminal['actual_opened_filepath'] == str(args.restored_source), 'Opened explicit restored filepath')
        c.require(terminal['source_saved'] is False and terminal['rebuild_performed'] is False and terminal['images'] == 0 and
                  terminal['world_loaded'] is False and terminal['world_integration_allowed'] is False and
                  terminal['visual_acceptance'] is False, 'Read-only source scope')
        c.require(terminal['restored_tree_unchanged'] is True and terminal['canonical_source_unchanged'] is True and
                  terminal['source_sha256'] == r.EXPECTED[r.SOURCE_REL][1] and
                  terminal['source_bytes'] == r.EXPECTED[r.SOURCE_REL][0], 'Unchanged source identities')
        reference = c.read(c.ROOT / r.RAW_REL)
        # Historical numeric PIDs may be reused. run_child's new Popen and
        # wait4 observation bind this fresh launch to terminal/raw PID above.
        binding = c.read(c.BINDING_PATH)
        c.require(terminal['validation'] == c.validate_raw(raw, binding), 'Unchanged full contract independently reapplied')
        r.same_raw(raw, reference)
        c.require(terminal['raw_equal_except_pid_affinity'] is True and
                  terminal['original_build_raw_sha256'] == r.EXPECTED[r.RAW_REL][1], 'Actual full raw equality provenance')
        outputs = r.tree_identity(output)
        report.update(passed=True, state='completed', raw_equal_except_pid_affinity=True,
                      raw_sha256=c.sha(rawpath), validation=terminal['validation'],
                      original_build_raw_sha256=r.EXPECTED[r.RAW_REL][1], actual_opened_filepath=terminal['actual_opened_filepath'])
    except BaseException:
        report.update(passed=False, state='failed', error=traceback.format_exc())
    finally:
        try:
            _, changed, errors = support.inspect_inputs(pins)
            after, restored_after = r.protected_identity(), r.restore_identity(args.restore_root, args.restored_source)
            support.atomic_json(run / 'protected-after.json', after)
            support.atomic_json(run / 'restored-after.json', restored_after)
            report.update(frozen_inputs_unchanged=bool(pins and not changed and not errors), changed_inputs=changed, input_errors=errors,
                          protected_originals_unchanged=bool(before and before == after),
                          restored_tree_unchanged=bool(restored_before and restored_before == restored_after),
                          canonical_source_sha256=c.sha(c.SOURCE), restored_source_sha256=c.sha(args.restored_source),
                          native_outputs_unchanged=bool(outputs and outputs == r.tree_identity(run / 'outputs')))
            report['passed'] = bool(report['passed'] and report['frozen_inputs_unchanged'] and
                                    report['protected_originals_unchanged'] and report['restored_tree_unchanged'] and
                                    report['native_outputs_unchanged'] and
                                    report['canonical_source_sha256'] == report['restored_source_sha256'] == r.EXPECTED[r.SOURCE_REL][1])
        except BaseException:
            report.update(passed=False, finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL, 0)
        for sig, handler in handlers.items(): signal.signal(sig, handler)
        elapsed = time.monotonic() - started
        if elapsed > TOTAL_SECONDS: report.update(passed=False, budget_overrun=True)
        report.update(state='completed' if report['passed'] else 'failed', total_wall_seconds=elapsed,
                      actual_wrapper_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      actual_wrapper_exit_code=0 if report['passed'] else 1)
        support.atomic_json(run / 'wrapper-report.json', report)
        (run / 'exit-code.txt').write_text(str(report['actual_wrapper_exit_code']) + '\n')
    return report['actual_wrapper_exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
