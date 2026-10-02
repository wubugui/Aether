"""Regression driver: original pure tests and real short owned Python processes."""
import contextlib, copy, hashlib, io, json, os, signal, subprocess, sys, tempfile, time, unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(HERE.parent/'source-runner-v2'))
import test_runner58l_v2 as previous
import run58l_v3 as runner
import deadline58l_v3 as deadline
from types import SimpleNamespace


class IdentityTests(unittest.TestCase):
    def test_pin_rejects_changed_identity(self):
        owned=deadline.Owned()
        try:
            row=deadline.metadata(os.getpid());row['starttime']+=1
            with self.assertRaisesRegex(RuntimeError,'identity mismatch'):
                owned.pin(os.getpid(),'fixture',row)
        finally:owned.close()

    def test_no_unknown_or_supervisor_signal(self):
        owned=deadline.Owned()
        try:
            for pid in (os.getpid(),999999999):
                with self.assertRaisesRegex(RuntimeError,'unregistered'):
                    owned.kill(pid,0)
        finally:owned.close()

    def test_reused_pid_retired_without_signaling_replacement(self):
        owned=deadline.Owned();fake=999999999;real_metadata=deadline.metadata
        old=dict(pid=fake,ppid=os.getpid(),pgid=fake,sid=fake,starttime=1,rss_kib=1)
        replacement=dict(old,ppid=1,starttime=2)
        owned.rows[fake]=old;owned.fds[fake]=os.dup(owned.fds[os.getpid()])
        try:
            with patch.object(deadline,'metadata',side_effect=lambda p:replacement if p==fake else real_metadata(p)),patch.object(deadline.signal,'pidfd_send_signal',side_effect=AssertionError('Never signal PID replacement')):
                rows=owned.scan()
                self.assertNotIn(fake,rows);self.assertNotIn(fake,owned.fds)
                with self.assertRaisesRegex(RuntimeError,'unregistered'):owned.kill(fake,0)
        finally:owned.close()

    def test_preexisting_child_not_signaled_or_reaped(self):
        p=subprocess.Popen([sys.executable,'-B','-c','import time; time.sleep(.15)'])
        try:
            with patch.object(deadline.signal,'pidfd_send_signal',side_effect=AssertionError('Must not signal pre-existing child')):
                code,row=deadline.supervise(lambda:0,started=time.monotonic(),limit=.2,finish=lambda r:None)
            self.assertEqual(code,1);self.assertIn('pre-existing',row['error']);self.assertIsNone(p.poll())
            self.assertEqual(p.wait(timeout=1),0)
        finally:
            if p.poll() is None:p.kill();p.wait()

    def test_unobservable_pidfd_is_rejected_before_fork(self):
        with patch.object(deadline.os,'pidfd_open',side_effect=OSError('fixture unavailable')):
            with patch.object(deadline.os,'fork',side_effect=AssertionError('Must not create worker')):
                code,row=deadline.supervise(lambda:0,started=time.monotonic(),limit=.2,finish=lambda r:None)
        self.assertEqual(code,1);self.assertFalse(row['passed']);self.assertNotIn('worker_pid',row)

    def test_failed_cleanup_is_bounded_and_never_passes(self):
        # No real child or signal: inject an unkillable WNOHANG child to verify
        # the failure bound. Real kill/reap is separately tested below.
        root=os.getpid();child=999999999
        row=dict(pid=child,ppid=root,pgid=child,sid=child,starttime=1,rss_kib=1)
        class FakeOwned:
            def __init__(self):self.root=root;self.rows={root:{'pid':root,'rss_kib':1},child:row};self.history=[];self.kills=[]
            def scan(self):return self.rows
            def pin(self,*a):return row
            def kill(self,*a):self.kills.append(a)
            def close(self):pass
        class Endpoint:
            def __init__(self):self.first=True
            def setblocking(self,*a):pass
            def settimeout(self,*a):pass
            def recv(self,*a):
                if self.first:self.first=False;return json.dumps(row).encode()
                raise BlockingIOError()
            def send(self,*a):pass
            def close(self):pass
        start=time.monotonic()
        with patch.object(deadline,'Owned',FakeOwned),patch.object(deadline.os,'fork',return_value=child),patch.object(deadline.socket,'socketpair',return_value=(Endpoint(),Endpoint())),patch.object(deadline.os,'wait4',return_value=(0,0,None)),patch.object(deadline,'CLEANUP_SECONDS',.03):
            code,result=deadline.supervise(lambda:0,started=start,limit=.02,finish=lambda r:None)
        self.assertEqual(code,1);self.assertFalse(result['passed']);self.assertFalse(result['all_owned_children_reaped'])
        self.assertTrue(result['cleanup_errors']);self.assertLess(time.monotonic()-start,.25)


def run_processes():
    root=Path(tempfile.mkdtemp(prefix='aether-v3-regression-'))
    observations=[]
    cases=('launcher_normal','old_counterexample','normal','timeout_tree','adopted_grandchild','registered_normal',
           'registered_tree','register_failure','missing_metadata','late_worker','late_receipt','receipt_error','rss_limit')
    for case in cases:
        out=root/case;out.mkdir();start=time.monotonic()
        with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
            p=subprocess.Popen([sys.executable,'-B',str(HERE/'process_fixture.py'),case,str(out)],stdout=stdout,stderr=stderr)
            code=p.wait(timeout=5)
        row=dict(case=case,supervisor_pid=p.pid,actual_exit_code=code,wall_seconds=time.monotonic()-start,
                 process_exit_observed=True,directory=str(out))
        row['records']={str(f.relative_to(out)):f.read_text() for f in out.rglob('*') if f.is_file()}
        receipt_path=next(out.glob('cloud-evidence/*/supervisor-terminal.json')) if case=='launcher_normal' else out/'receipt.json'
        if receipt_path.exists():row['supervisor_terminal_sha256']=hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        observations.append(row)
        (root/'observations.json').write_text(json.dumps(observations,indent=2)+'\n')
        if case=='launcher_normal':
            check=unittest.TestCase();receipt=json.loads(receipt_path.read_text())
            check.assertEqual(code,0);check.assertLess(row['wall_seconds'],120)
            check.assertEqual(receipt['supervisor_pid'],p.pid);check.assertTrue(deadline.accepted(receipt))
            terminal=out/'source-runner-v3/source-terminal.json';wrapper=receipt_path.parent/'wrapper-report.json'
            check.assertEqual(receipt['terminal_sha256'],hashlib.sha256(terminal.read_bytes()).hexdigest())
            check.assertEqual(receipt['wrapper_report_sha256'],hashlib.sha256(wrapper.read_bytes()).hexdigest())
            check.assertEqual(terminal.read_bytes(),wrapper.read_bytes());check.assertFalse(json.loads(terminal.read_text())['passed'])
            print('PASS actual launcher/Popen/SHA',p.pid,'exit',code,'wall',round(row['wall_seconds'],6),flush=True)
            continue
        data=json.loads(row['records']['returned.json']);r=data['result']
        check=unittest.TestCase()
        check.assertEqual(r['supervisor_pid'],p.pid)
        check.assertEqual(code,0 if case in ('normal','registered_normal') else 1)
        check.assertEqual(data['code'],code)
        if case=='old_counterexample':
            check.assertFalse(data['children_file_exists'])
            check.assertTrue(all(set(s['rows'])=={str(p.pid)} for s in data['trace']))
            check.assertGreaterEqual(row['wall_seconds'],.5)
            grand=json.loads(row['records']['grandchild.json'])['pid']
            check.assertIn(dict(pid=grand,returncode=0),r['forced_reaped'])
        else:
            check.assertLess(row['wall_seconds'],1.5)
            if case!='missing_metadata':check.assertTrue(r['all_owned_children_reaped'])
        if case in ('timeout_tree','registered_tree'):
            check.assertTrue(r['timeout_triggered']);check.assertFalse(r['passed'])
            grand=json.loads(row['records']['grandchild.json'])['pid']
            killed={a['pid'] for a in r['forced_kills']}
            check.assertIn(grand,killed);check.assertIn(r['worker_pid'],killed)
            check.assertTrue(all(a['returncode']==-9 for a in r['forced_reaped']))
            check.assertNotIn('natural_exit.json',row['records'])
            need=3 if case=='timeout_tree' else 4
            sample=max(r['process_samples'],key=lambda s:len(s['processes']))
            check.assertGreaterEqual(len(sample['processes']),need)
            check.assertIn(grand,{a['pid'] for a in sample['processes']})
            check.assertEqual(sample['aggregate_rss_kib'],sum(a['rss_kib'] for a in sample['processes']))
            check.assertTrue(all(a['rss_kib']>0 for a in sample['processes']))
        if case=='adopted_grandchild':
            # Parent's durable fork result exists even if cleanup kills the orphan
            # before that child's own optional first write can execute.
            grand=json.loads(row['records']['worker.json'])['grandchild']
            check.assertTrue(any(a['pid']==grand and a['ppid']==p.pid for a in r['owned_process_history']))
            check.assertTrue(any(a['pid']==grand and a['returncode']==-9 for a in r['forced_reaped']))
        if case.startswith('registered_'):
            check.assertEqual(len(r['native_registrations']),1)
            native=r['native_registrations'][0]
            check.assertEqual(native['ppid'],r['worker_pid']);check.assertEqual(native['pid'],native['pgid']);check.assertEqual(native['pid'],native['sid'])
        if case=='register_failure':
            child=json.loads(row['records']['python-child-result.json'])
            check.assertIn('registration failure',child['exception']);check.assertFalse(child['native_exit_observed'])
            check.assertIn('actual returncode=-9',child['exception'])
        if case=='rss_limit':check.assertTrue(r['rss_limit_triggered'])
        if case in ('late_worker','late_receipt','receipt_error'):
            check.assertFalse(r['passed']);check.assertTrue(r['all_owned_children_reaped'])
            check.assertIn('one.json',row['records']);check.assertIn('two.json',row['records'])
        print('PASS process',case,'exit',code,'wall',round(row['wall_seconds'],6),flush=True)
    result=dict(scope='actual short pure Python processes; never engine/native asset work',
                deadline_sha256=hashlib.sha256(Path(deadline.__file__).read_bytes()).hexdigest(),
                fixture_sha256=hashlib.sha256((HERE/'process_fixture.py').read_bytes()).hexdigest(),
                retained_directory=str(root),observations=observations)
    output=Path(os.environ.get('AETHER_V3_EVIDENCE_DIR',str(HERE)))/('process-evidence-optimized.json' if sys.flags.optimize else 'process-evidence-normal.json')
    output.write_text(json.dumps(result,indent=2)+'\n')
    return len(cases)


def main():
    start=time.monotonic();count=0
    # All original 42 tests, including actual original R1/R2/R3 counterexamples.
    # Redirect their otherwise package-local TemporaryDirectory to /tmp.
    with tempfile.TemporaryDirectory(prefix='aether-v3-original-') as temp:
        previous.HERE=Path(temp)
        with patch.object(previous.r.support,'run_child',side_effect=AssertionError('No engine in original regression')):
            result=unittest.TextTestRunner(verbosity=2).run(previous.suite())
        if not result.wasSuccessful():return 1
        count+=result.testsRun
        # Same R1/R2 fixtures now point at the v3 module; no copied validators.
        previous.r=runner;previous.d=deadline
        suite=unittest.TestSuite()
        for cls in (previous.ExerciseTests,previous.ProtectionTests,IdentityTests):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(cls))
        with patch.object(runner.support,'run_child',side_effect=AssertionError('No engine in v3 regression')):
            result=unittest.TextTestRunner(verbosity=2).run(suite)
        if not result.wasSuccessful():return 1
        count+=result.testsRun
    count+=run_processes()
    print('TOTAL',count,'passed; actual wall',time.monotonic()-start,flush=True)
    return 0


if __name__=='__main__':raise SystemExit(main())
