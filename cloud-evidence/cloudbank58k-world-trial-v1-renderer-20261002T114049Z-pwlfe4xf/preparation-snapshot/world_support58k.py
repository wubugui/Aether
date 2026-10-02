"""Shared fail-closed process/evidence helpers. Importing never starts an engine."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import resource
import time

MAX_RSS_KIB = 3145728

def resident_kib(pid):
    try:
        for line in (Path('/proc') / str(pid) / 'status').read_text().splitlines():
            if line.startswith('VmRSS:'):return int(line.split()[1])
    except FileNotFoundError:pass
    return 0

STOP_SIGNALS = {signal.SIGINT, signal.SIGTERM, signal.SIGALRM}


def sha(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    temporary.replace(path)


def strict_json(path: Path) -> dict:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('Nonfinite JSON number: ' + value)
    def finite(value):
        number = float(value)
        if not math.isfinite(number):
            invalid(value)
        return number
    result = json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid, parse_float=finite)
    if not isinstance(result, dict):
        raise ValueError('Expected JSON object: ' + str(path))
    return result


def inspect_inputs(expected: dict[str, str]) -> tuple[dict, list, list]:
    """Observe every original path, even when one is missing/unreadable/changed."""
    observed, changed, errors = {}, [], []
    for raw, original in expected.items():
        path = Path(raw)
        try:
            observed[raw] = sha(path) if path.is_file() and not path.is_symlink() else None
        except OSError as exc:
            observed[raw] = None
            errors.append({'path': raw, 'error': repr(exc)})
        if observed[raw] != original:
            changed.append(raw)
    return observed, changed, errors


def error_lines(paths: list[Path]) -> list[str]:
    return [line for path in paths for line in path.read_text(errors='replace').splitlines()
            if any(token in line for token in ('ERROR:', 'SCRIPT ERROR:', 'Parse Error:'))
            or 'leaked' in line.lower()]


def run_child(command: list[str], out: Path, env: dict, cwd: Path, timeout: float,
              label: str, heartbeat: Path | None = None, *, wall_timeout_limit: int = 720) -> dict:
    """Own the child's PID before delivering cancellation; always kill/reap on error.

    Terminal reports preserve the actual wait4 exit status. The timeout is a hard
    child wall limit, with no unreported termination-grace extension. SIGKILL of
    this Python process or an unwritable filesystem cannot promise a report.
    """
    if len(list(Path('/proc/self/task').iterdir())) != 1:
        raise RuntimeError('preexec_fn requires a single-threaded supervising wrapper')
    cpus = sorted(os.sched_getaffinity(0))[:2]
    if len(cpus) != 2:
        raise RuntimeError('Two available CPUs are required')
    if type(wall_timeout_limit) is not int or wall_timeout_limit not in (720, 1020):
        raise ValueError('Only the default720 or explicit1020 process cap is supported')
    if (type(timeout) not in (int, float) or not math.isfinite(timeout) or
            not 0 < timeout <= wall_timeout_limit):
        raise ValueError('Child timeout must be finite, positive and within the explicitly selected cap')
    started = time.monotonic()
    child = None
    previous_handlers = {}
    result = {'status': 'not_started', 'command': command, 'cpu_affinity': cpus,
              'wall_timeout_seconds': timeout, 'wall_timeout_limit_seconds': wall_timeout_limit,
              'timeout_triggered': False,
              'wrapper_received_signal': None, 'returncode': None,
              'native_exit_observed': False, 'max_rss_kib': None, 'rss_limit_triggered': False, 'max_aggregate_observed_rss_kib': 0}
    previous_mask = signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)

    def kill_child():
        if child is not None and child.returncode is None:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    def stop(signum, _frame):
        result['wrapper_received_signal'] = signum
        kill_child()

    def setup_child():
        os.sched_setaffinity(0, cpus)
        # Popen resets caught handlers to default during exec. Unblock the two
        # signals only after affinity is set, before entering the executable.
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)

    def wait_child(flags):
        while True:
            try:
                waited, status, usage = os.wait4(child.pid, flags)
                break
            except InterruptedError:
                continue
        if waited:
            child.returncode = os.waitstatus_to_exitcode(status)
            result.update(returncode=child.returncode, native_exit_observed=True,
                          max_rss_kib=usage.ru_maxrss,
                          signal=-child.returncode if child.returncode < 0 else None)
        return bool(waited)

    try:
        for sig in STOP_SIGNALS:
            previous_handlers[sig] = signal.signal(sig, stop)
        with (out / f'{label}.stdout.log').open('wb') as stdout, (out / f'{label}.stderr.log').open('wb') as stderr:
            child = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env,
                                     cwd=cwd, start_new_session=True, preexec_fn=setup_child)
            result.update(status='running', pid=child.pid)
            # No unowned-child cancellation window between Popen and handlers.
            signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
            atomic_json(out / f'{label}.process.json', result)
            last_heartbeat = -1.0
            while not wait_child(os.WNOHANG):
                now = time.monotonic()
                aggregate = resident_kib(child.pid) + resident_kib(os.getpid())
                result['max_aggregate_observed_rss_kib'] = max(result['max_aggregate_observed_rss_kib'], aggregate)
                if aggregate > MAX_RSS_KIB:
                    result['rss_limit_triggered'] = True
                    kill_child()
                if now - started >= timeout:
                    result['timeout_triggered'] = True
                    kill_child()
                if now - last_heartbeat >= 1.0:
                    exists = heartbeat is not None and heartbeat.is_file()
                    atomic_json(out / f'{label}.progress.json', {
                        'status': 'running', 'diagnostic_only': True,
                        'completion_authority': 'wrapper-report.json and complete native report',
                        'pid': child.pid, 'process_wall_seconds': now - started,
                        'wall_timeout_seconds': timeout,
                        'engine_progress_exists': exists,
                        'engine_progress_age_seconds': max(0.0, time.time() - heartbeat.stat().st_mtime) if exists else None,
                        'stop_requested': result['wrapper_received_signal'] is not None or result['timeout_triggered'],
                    })
                    last_heartbeat = now
                time.sleep(.025)
            result['status'] = 'finished'
    except BaseException as exc:
        result.update(status='wrapper_exception', exception=repr(exc))
    finally:
        # Keep our non-raising signal handler installed throughout reap/report.
        try:
            if child is not None and child.returncode is None:
                kill_child()
                wait_child(0)
        except BaseException as exc:
            result.update(status='reap_error', reap_error=repr(exc))
        result['wall_seconds'] = time.monotonic() - started
        if result['max_rss_kib'] is not None and result['max_rss_kib'] + resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > MAX_RSS_KIB:
            result['rss_limit_triggered'] = True
        if result['wall_seconds'] > timeout:
            result['timeout_triggered'] = True
        for name, report in [(f'{label}.process.json', result), (f'{label}.progress.json', {
                'status': result['status'], 'diagnostic_only': True,
                'process_wall_seconds': result['wall_seconds'], 'returncode': result['returncode'],
                'native_exit_observed': result['native_exit_observed'],
                'completion_authority': 'wrapper-report.json and complete native report'})]:
            try:
                atomic_json(out / name, report)
            except BaseException as exc:
                result.setdefault('terminal_report_errors', []).append(repr(exc))
        signal.pthread_sigmask(signal.SIG_BLOCK, STOP_SIGNALS)
        for sig, handler in previous_handlers.items():
            signal.signal(sig, handler)
        signal.pthread_sigmask(signal.SIG_SETMASK, previous_mask)
    return result


def process_passed(row: dict) -> bool:
    return (row.get('status') == 'finished' and row.get('native_exit_observed') is True
            and row.get('returncode') == 0 and row.get('wrapper_received_signal') is None
            and row.get('timeout_triggered') is False and row.get('rss_limit_triggered') is False and not row.get('terminal_report_errors'))
