"""Linux, one operation only: observe its real exit after every terminal write.

No native launch here. The source worker retains bounded_support58k ownership
of native children. This extra parent checks aggregate RSS for all three levels.
"""
from __future__ import annotations
import ctypes, os, resource, signal, time, traceback
from pathlib import Path

MAX_RSS_KIB = 1572864


def process_tree(root):
    """Read only this owned process and descendants via their task children lists."""
    rows={};todo=[root]
    while todo:
        pid=todo.pop()
        if pid in rows:continue
        path=Path('/proc')/str(pid)
        try:
            lines=path.joinpath('status').read_text().splitlines()
            rows[pid]=next((int(line.split()[1]) for line in lines if line.startswith('VmRSS:')),0)
            for task in path.joinpath('task').iterdir():
                try:todo.extend(int(x) for x in task.joinpath('children').read_text().split())
                except FileNotFoundError:pass
        except FileNotFoundError:continue
    return rows


def accepted(record):
    """A prepared report alone is never a success terminal."""
    return (record.get('state') == 'completed' and record.get('passed') is True
            and record.get('worker_exit_observed') is True and record.get('worker_returncode') == 0
            and record.get('worker_observed_wall_seconds', float('inf')) < record['limit_seconds']
            and record.get('receipt_ready_wall_seconds', float('inf')) < record['limit_seconds']
            and not record.get('error') and not record.get('timeout_triggered')
            and not record.get('rss_limit_triggered') and record.get('all_owned_children_reaped') is True)


def supervise(operation, *, started, limit, finish, clock=time.monotonic):
    """fork/wait4 the complete operation including both prepared terminal writes.

finish(record) persists one external process receipt. Its IO remains under this
parent's deadline; the executable keeps the alarm armed until os._exit. Receipt
completion times are named observations, not a fabricated self-exit timestamp.
The caller must require the actual launch exit code zero as well as this receipt.
"""
    result = dict(state='failed', passed=False, limit_seconds=limit, supervisor_pid=os.getpid(),
                  worker_exit_observed=False, worker_returncode=None, timeout_triggered=False,
                  rss_limit_triggered=False, max_aggregate_rss_kib=0, all_owned_children_reaped=False,
                  completion_authority='real wait4 after all phase IO plus launcher exit zero')
    child = None
    handlers = {}
    # Adopt an orphan only if forced cleanup interrupts the worker's normal reap.
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'PR_SET_CHILD_SUBREAPER')

    def stopped(number, frame):
        result['timeout_triggered'] |= number == signal.SIGALRM
        raise InterruptedError('Supervisor stop signal ' + str(number))

    def check_budget():
        if clock() - started >= limit:
            result['timeout_triggered'] = True
            raise TimeoutError('Whole source phase deadline, including terminal IO')

    def kill_owned():
        # Children have separate sessions; kill every actual descendant, child last.
        owned = process_tree(os.getpid())
        for pid in sorted((p for p in owned if p not in (os.getpid(), child)), reverse=True) + ([child] if child else []):
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    try:
        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGALRM):
            handlers[sig] = signal.signal(sig, stopped)
        check_budget()
        signal.setitimer(signal.ITIMER_REAL, limit - (clock() - started))
        oldmask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT, signal.SIGTERM, signal.SIGALRM})
        try:
            child = os.fork()
            if child == 0:
                # Native admission uses this actual worker PID, never the supervisor.
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
                try:
                    code = operation()
                except BaseException:
                    traceback.print_exc()
                    code = 1
                os._exit(code)
        finally:
            if child != 0:
                signal.pthread_sigmask(signal.SIG_SETMASK, oldmask)
        result['worker_pid'] = child
        while True:
            check_budget()
            rss = sum(process_tree(os.getpid()).values())
            result['max_aggregate_rss_kib'] = max(result['max_aggregate_rss_kib'], rss)
            if rss > MAX_RSS_KIB:
                result['rss_limit_triggered'] = True
                raise MemoryError('Supervisor + worker + all native descendants exceeded 1.5 GiB')
            waited, status, usage = os.wait4(child, os.WNOHANG)
            if waited:
                result.update(worker_exit_observed=True, worker_returncode=os.waitstatus_to_exitcode(status),
                              worker_observed_wall_seconds=clock()-started, worker_peak_rss_kib=usage.ru_maxrss)
                child = None
                break
            time.sleep(.01)
        check_budget()
        # Worker must have reaped native children through the original owner.
        if len(process_tree(os.getpid())) != 1:
            raise RuntimeError('Unreaped descendant after complete source worker')
        result.update(all_owned_children_reaped=True, receipt_ready_wall_seconds=clock()-started,
                      state='completed' if result['worker_returncode'] == 0 else 'failed',
                      passed=result['worker_returncode'] == 0)
        finish(result)
        check_budget()  # Includes hashes, both phase terminals, receipt write/flush/fsync.
        result['parent_after_receipt_wall_seconds'] = clock()-started  # returned, not rewritten into receipt
        return 0 if accepted(result) else 1, result
    except BaseException:
        result.update(passed=False, state='failed', error=traceback.format_exc())
        kill_owned()
        # Failure cleanup has no success path; retain actual wait statuses.
        reaped = []
        while True:
            try:
                pid, status, usage = os.wait4(-1, 0)
                reaped.append(dict(pid=pid, returncode=os.waitstatus_to_exitcode(status)))
                if pid == child:
                    result.update(worker_exit_observed=True, worker_returncode=os.waitstatus_to_exitcode(status),
                                  worker_observed_wall_seconds=clock()-started)
            except ChildProcessError:
                break
            except InterruptedError:
                continue
        result.update(forced_reaped=reaped, all_owned_children_reaped=len(process_tree(os.getpid()))==1,
                      receipt_ready_wall_seconds=clock()-started)
        try:
            finish(result)
        except BaseException:
            traceback.print_exc()  # no successful receipt is sufficient without launch exit zero
        return 1, result
    finally:
        # The executable installs a hard final-tail alarm immediately on return.
        # There is no successful file operation after the final budget check.
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
