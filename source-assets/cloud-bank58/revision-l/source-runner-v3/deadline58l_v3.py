"""One source/views worker, explicit native registration, identity-safe Linux cleanup.

Only process identity/relationship/RSS metadata is read. Never read environments,
command lines, handles or task/children. No engine is launched by this module.
"""
from __future__ import annotations
from contextlib import contextmanager
import ctypes, json, os, resource, signal, socket, time, traceback
from pathlib import Path
from types import SimpleNamespace

MAX_RSS_KIB = 1572864
CLEANUP_SECONDS = 1.0  # Failure-only bound, never extends a successful stage.
POLL_SECONDS = .005
_registration = None


def metadata(pid):
    """Extract only required fields; discard the stat comm and unrelated data."""
    try:
        raw = (Path('/proc') / str(pid) / 'stat').read_text()
    except FileNotFoundError:
        return None
    fields = raw[raw.rfind(')') + 2:].split()
    row = dict(pid=int(pid), state=fields[0], ppid=int(fields[1]),
               pgid=int(fields[2]), sid=int(fields[3]), starttime=int(fields[19]),
               rss_kib=int(fields[21]) * os.sysconf('SC_PAGE_SIZE') // 1024)
    if row['rss_kib'] < 0 or row['starttime'] <= 0:
        raise RuntimeError('Required process identity/RSS unavailable')
    return row


class Owned:
    """Pin only this supervisor and its actual descendants; pidfds defeat reuse."""
    def __init__(self):
        if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
            raise RuntimeError('Identity-safe pidfd signaling unavailable')
        self.root = os.getpid()
        self.rows = {}
        self.fds = {}
        self.history = []
        self.kills = []
        self.pin(self.root, 'supervisor')

    def pin(self, pid, reason, expected=None):
        row = metadata(pid)
        if row is None:
            raise RuntimeError('Owned process disappeared before identity registration')
        if expected is not None and any(row[k] != expected[k] for k in ('pid', 'ppid', 'pgid', 'sid', 'starttime')):
            raise RuntimeError('Registration identity mismatch')
        if pid in self.rows:
            if row['starttime'] != self.rows[pid]['starttime']:
                raise RuntimeError('Owned PID reused before registration')
            return row
        fd = os.pidfd_open(pid)
        again = metadata(pid)
        if again is None or any(again[k] != row[k] for k in ('pid', 'ppid', 'pgid', 'sid', 'starttime')):
            os.close(fd)
            raise RuntimeError('Identity changed while opening pidfd')
        self.rows[pid], self.fds[pid] = row, fd
        self.history.append(dict(row, reason=reason))
        return row

    def scan(self):
        # Re-read known identities before following PPid; never trust a reused PID.
        current = {}
        for pid, old in list(self.rows.items()):
            row = metadata(pid)
            if row is not None and row['starttime'] == old['starttime']:
                current[pid] = row
            else:
                if pid == self.root:
                    raise RuntimeError('Supervisor identity no longer observable')
                os.close(self.fds.pop(pid))
                self.rows.pop(pid)
        # PPid closure also finds adopted children after the worker was killed.
        # Unrelated metadata is immediately discarded, never logged or retained.
        while True:
            added = False
            for entry in Path('/proc').iterdir():
                if not entry.name.isdecimal():
                    continue
                pid = int(entry.name)
                if pid in current:
                    continue
                row = metadata(pid)
                if row is None or row['ppid'] not in current:
                    continue
                parent = metadata(row['ppid'])
                if parent is None or parent['starttime'] != current[row['ppid']]['starttime']:
                    continue
                try:
                    current[pid] = self.pin(pid, 'observed_owned_ppid', row)
                except (ProcessLookupError, FileNotFoundError):
                    continue
                except RuntimeError as exc:
                    if str(exc) == 'Registration identity mismatch':
                        continue  # Reparented during observation; rediscover next pass.
                    raise
                added = True
            if not added:
                break
        return current

    def kill(self, pid, elapsed):
        if pid == self.root or pid not in self.fds:
            raise RuntimeError('Refusing signal to unregistered process')
        row = self.rows[pid]
        # The open pidfd already names this exact process even after PID reuse.
        # Cleanup still reaches known owners if metadata becomes unavailable.
        try:
            signal.pidfd_send_signal(self.fds[pid], signal.SIGKILL)
            self.kills.append(dict(pid=pid, starttime=row['starttime'], wall_seconds=elapsed, signal=9))
        except ProcessLookupError:
            pass

    def close(self):
        for fd in self.fds.values():
            os.close(fd)
        self.fds.clear()


def accepted(record):
    return (record.get('state') == 'completed' and record.get('passed') is True
            and record.get('worker_exit_observed') is True and record.get('worker_returncode') == 0
            and 0 <= record.get('worker_observed_wall_seconds', float('inf')) < record['limit_seconds']
            and record.get('receipt_ready_wall_seconds', float('inf')) < record['limit_seconds']
            and not record.get('error') and not record.get('timeout_triggered')
            and not record.get('rss_limit_triggered') and record.get('all_owned_children_reaped') is True
            and record.get('ownership_observable') is True)


@contextmanager
def registered_native_launches(support):
    """Intercept only the existing support's Popen return; command/session unchanged."""
    if _registration is None:
        raise RuntimeError('Native launch requires live owning supervisor registration')
    original = support.subprocess
    def launch(*args, **kwargs):
        child = original.Popen(*args, **kwargs)
        try:
            row = metadata(child.pid)
            if row is None or row['ppid'] != os.getpid() or row['pgid'] != child.pid or row['sid'] != child.pid:
                raise RuntimeError('Native must be this worker\'s actual new-session child')
            _registration.send(json.dumps(row).encode())
            if _registration.recv(32) != b'owned':
                raise RuntimeError('Native registration not acknowledged')
        except BaseException as registration_error:
            # This is our just-created, unreaped direct Popen child. No PID reuse
            # is possible before wait; never signal any guessed group or process.
            if child.returncode is None:
                try: os.kill(child.pid, signal.SIGKILL)
                except ProcessLookupError: pass
                until = time.monotonic() + CLEANUP_SECONDS
                while time.monotonic() < until:
                    pid, status = os.waitpid(child.pid, os.WNOHANG)
                    if pid:
                        child.returncode = os.waitstatus_to_exitcode(status)
                        break
                    time.sleep(POLL_SECONDS)
            raise RuntimeError('Native registration failed; owned direct child pid='+str(child.pid)+
                               ', actual returncode='+str(child.returncode)+', cause='+repr(registration_error)) from registration_error
        return child
    support.subprocess = SimpleNamespace(Popen=launch)
    try:
        yield
    finally:
        support.subprocess = original


def supervise(operation, *, started, limit, finish, clock=time.monotonic):
    """Cover operation, terminal IO, actual worker wait4 and receipt IO in one cap."""
    global _registration
    result = dict(state='failed', passed=False, limit_seconds=limit, supervisor_pid=os.getpid(),
                  worker_exit_observed=False, worker_returncode=None, timeout_triggered=False,
                  rss_limit_triggered=False, max_aggregate_rss_kib=0, all_owned_children_reaped=False,
                  ownership_observable=False, process_samples=[], native_registrations=[],
                  completion_authority='real wait4 after all phase IO plus launcher exit zero')
    owned = None
    success_return = False
    child = None
    handlers = {}
    parent_socket = worker_socket = None
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER')

    def stopped(number, frame):
        result['timeout_triggered'] |= number == signal.SIGALRM
        raise InterruptedError('Supervisor stop signal ' + str(number))

    def check_budget():
        if clock() - started >= limit:
            result['timeout_triggered'] = True
            raise TimeoutError('Whole stage deadline including terminal IO')

    def registrations():
        while True:
            try: data = parent_socket.recv(4096)
            except BlockingIOError: break
            if not data: break
            row = json.loads(data)
            if row['ppid'] != result['worker_pid']:
                raise RuntimeError('Registration is not the actual worker child')
            actual = owned.pin(row['pid'], 'explicit_native', row)
            if actual['pgid'] != actual['pid'] or actual['sid'] != actual['pid']:
                raise RuntimeError('Registered native lacks its own session')
            result['native_registrations'].append(actual)
            parent_socket.send(b'owned')

    def observed(pid, status, usage):
        row = dict(pid=pid, returncode=os.waitstatus_to_exitcode(status), wall_seconds=clock()-started,
                   peak_rss_kib=usage.ru_maxrss)
        if pid == result.get('worker_pid'):
            result.update(worker_exit_observed=True, worker_returncode=row['returncode'],
                          worker_observed_wall_seconds=row['wall_seconds'], worker_peak_rss_kib=usage.ru_maxrss)
        return row

    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            handlers[sig] = signal.signal(sig, stopped)
        check_budget()
        signal.setitimer(signal.ITIMER_REAL, limit-(clock()-started))
        owned = Owned()
        for entry in Path('/proc').iterdir():
            if entry.name.isdecimal():
                row = metadata(int(entry.name))
                if row is not None and row['ppid'] == owned.root:
                    raise RuntimeError('Supervisor must start without pre-existing children')
        result['ownership_observable'] = True
        parent_socket, worker_socket = socket.socketpair(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        parent_socket.setblocking(False)
        worker_socket.settimeout(max(.001, limit-(clock()-started)))
        oldmask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM, signal.SIGALRM})
        try:
            child = os.fork()
            if child == 0:
                parent_socket.close()
                owned.close()
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
                try:
                    os.setsid()
                    worker_socket.send(json.dumps(metadata(os.getpid())).encode())
                    if worker_socket.recv(32) != b'start':
                        raise RuntimeError('Worker not registered')
                    _registration = worker_socket
                    code = operation()
                except BaseException:
                    traceback.print_exc()
                    code = 1
                os._exit(code)
        finally:
            if child != 0:
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
        worker_socket.close(); worker_socket = None
        result['worker_pid'] = child
        while True:
            check_budget()
            try:
                row = json.loads(parent_socket.recv(4096))
                break
            except BlockingIOError:
                time.sleep(POLL_SECONDS)
        if row['pid'] != child or row['ppid'] != owned.root or row['pgid'] != child or row['sid'] != child:
            raise RuntimeError('Actual worker session identity mismatch')
        owned.pin(child, 'explicit_worker', row)
        parent_socket.send(b'start')
        while True:
            check_budget()
            registrations()
            rows = owned.scan()
            rss = sum(row['rss_kib'] for row in rows.values())
            result['max_aggregate_rss_kib'] = max(result['max_aggregate_rss_kib'], rss)
            # Retain membership changes and peak samples, not an unbounded trace.
            sample = dict(wall_seconds=clock()-started, aggregate_rss_kib=rss,
                          processes=[rows[p] for p in sorted(rows)])
            samples = result['process_samples']
            if not samples or [r['pid'] for r in samples[-1]['processes']] != sorted(rows) or rss > max(s['aggregate_rss_kib'] for s in samples):
                samples.append(sample)
            if rss > MAX_RSS_KIB:
                result['rss_limit_triggered'] = True
                raise MemoryError('Supervisor plus all actual descendants exceeded 1.5 GiB')
            pid, status, usage = os.wait4(child, os.WNOHANG)
            if pid:
                observed(pid, status, usage)
                child = None
                break
            time.sleep(POLL_SECONDS)
        check_budget()
        # Kernel wait status is also required; a proc snapshot alone is insufficient.
        rows = owned.scan()
        try:
            pid, status, usage = os.wait4(-1, os.WNOHANG)
        except ChildProcessError:
            pid = None
        if len(rows) != 1 or pid is not None:
            if pid:
                result.setdefault('unexpected_reaped', []).append(observed(pid, status, usage))
            raise RuntimeError('Worker left owned descendants; reject and clean up')
        result.update(all_owned_children_reaped=True, receipt_ready_wall_seconds=clock()-started,
                      state='completed' if result['worker_returncode'] == 0 else 'failed',
                      passed=result['worker_returncode'] == 0, owned_process_history=owned.history)
        finish(result)
        check_budget()
        result['parent_after_receipt_wall_seconds'] = clock()-started
        success_return = accepted(result)
        return (0 if success_return else 1), result
    except BaseException:
        result.update(passed=False, state='failed', error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL, 0)
        # Bounded failure cleanup repeatedly observes adopted descendants; never
        # blocking wait4(-1, 0), never assume one snapshot found the final child.
        cleanup_until = time.monotonic() + CLEANUP_SECONDS
        reaped = []
        cleanup_errors = []
        def cleanup_alarm(*_):
            raise TimeoutError('Bounded failure cleanup/receipt expired')
        signal.signal(signal.SIGALRM, cleanup_alarm)
        signal.setitimer(signal.ITIMER_REAL, CLEANUP_SECONDS)
        try:
            while owned is not None and (child is not None or 'worker_pid' in result) and time.monotonic() < cleanup_until:
                try:
                    rows = owned.scan()
                except BaseException as exc:
                    cleanup_errors.append('Metadata cleanup observation failed: '+repr(exc))
                    rows = owned.rows.copy()
                for pid in sorted(p for p in rows if p != owned.root):
                    owned.kill(pid, clock()-started)
                no_children = False
                while True:
                    try: pid, status, usage = os.wait4(-1, os.WNOHANG)
                    except ChildProcessError:
                        no_children = True
                        break
                    if not pid: break
                    reaped.append(observed(pid, status, usage))
                rows = owned.scan()
                if no_children and len(rows) == 1:
                    result['all_owned_children_reaped'] = True
                    break
                time.sleep(POLL_SECONDS)
            if not result['all_owned_children_reaped']:
                cleanup_errors.append('Owned children not proven reaped within failure bound')
            result.update(forced_reaped=reaped, forced_kills=owned.kills if owned else [],
                          owned_process_history=owned.history if owned else [],
                          cleanup_errors=cleanup_errors, cleanup_limit_seconds=CLEANUP_SECONDS,
                          receipt_ready_wall_seconds=clock()-started)
            finish(result)
        except BaseException:
            result.update(cleanup_errors=cleanup_errors+[traceback.format_exc()], forced_reaped=reaped,
                          forced_kills=owned.kills if owned else [], passed=False, state='failed')
            traceback.print_exc()
        return 1, result
    finally:
        if not success_return:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if parent_socket is not None: parent_socket.close()
        if worker_socket is not None: worker_socket.close()
        if owned is not None: owned.close()
        for sig, handler in handlers.items(): signal.signal(sig, handler)
