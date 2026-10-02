"""Short, pure Python process fixtures. Never invoke Blender/Godot/native code."""
import copy, json, os, signal, subprocess, sys, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'source-runner-v2'))
sys.path.insert(0,str(HERE.parents[1]/'revision-k/import-v1'))
import deadline58l_v3 as new
import deadline58l as old
import bounded_support58k as support
from types import SimpleNamespace


def main(case, directory):
    out=Path(directory);out.mkdir(exist_ok=True)
    if case=='launcher_normal':
        import run58l_v3 as runner
        runner.ROOT=out;runner.HERE=out/'source-runner-v3';runner.HERE.mkdir()
        runner.ORIGINAL=out/'source-v1';runner.ORIGINAL.mkdir()
        (out/'cloud-evidence').mkdir()
        # This is explicitly a text fixture, never a native source/model.
        source=runner.ORIGINAL/'source-placeholder.txt'
        sys.modules['geometry58l']=SimpleNamespace(SOURCE=source)
        (runner.HERE/'run58l_v3.py').write_bytes((HERE/'run58l_v3.py').read_bytes())
        def fake_phase(stage,run,started,limit):
            source.write_text('pure Python durability fixture, not native')
            admission=runner.HERE/(stage+'-attempt.json')
            support.atomic_json(admission,dict(stage=stage,wrapper_pid=os.getpid(),supervisor_pid=os.getppid()))
            row=dict(stage=stage,run=str(run),source=str(source),runner_version=runner.VERSION,
                     runner_sha256=support.sha(runner.HERE/'run58l_v3.py'),worker_pid=os.getpid(),supervisor_pid=os.getppid(),
                     admission_sha256=support.sha(admission),source_sha256=support.sha(source),source_bytes=source.stat().st_size,
                     prepared_passed=True,passed=False,state='awaiting_external_process_terminal',actual_wrapper_peak_rss_kib=1,stages=[])
            support.atomic_json(run/'wrapper-report.json',row)
            support.atomic_json(runner.HERE/(stage+'-terminal.json'),row)
            return 0
        runner.phase=fake_phase
        return runner.main(['--run-approved','source'])
    d=old if case=='old_counterexample' else new
    started=time.monotonic(); records=[]
    limit=.08 if case in ('old_counterexample','timeout_tree','late_worker','late_receipt') else .2
    if case in ('normal','registered_normal','register_failure'):limit=2
    def event(name, row):
        support.atomic_json(out/(name+'.json'),row)
    def fork_grandchild(sleep, exit_parent=False):
        pid=os.fork()
        if not pid:
            os.setsid();memory=bytearray(5*1024*1024)
            event('grandchild',dict(pid=os.getpid(),ppid=os.getppid(),started=time.monotonic(),rss=new.metadata(os.getpid())['rss_kib']))
            time.sleep(sleep)
            event('natural_exit',dict(pid=os.getpid(),ended=time.monotonic()))
            os._exit(0)
        event('worker',dict(pid=os.getpid(),ppid=os.getppid(),grandchild=pid))
        if exit_parent:os._exit(1)
        time.sleep(sleep+1)
    def operation():
        memory=bytearray(3*1024*1024)
        if case=='old_counterexample':fork_grandchild(.5)
        if case in ('timeout_tree','rss_limit'):fork_grandchild(2)
        if case=='adopted_grandchild':fork_grandchild(2,True)
        if case in ('registered_normal','registered_tree','register_failure'):
            command=[sys.executable,'-B','-c','import time; time.sleep(.025)']
            if case=='registered_tree':
                code="import os,time,json; from pathlib import Path; p=os.fork(); "
                code+="\nif not p:\n os.setsid(); m=bytearray(5*1024*1024); Path("+repr(str(out/'grandchild.json'))+").write_text(json.dumps(dict(pid=os.getpid(),ppid=os.getppid()))); time.sleep(2); os._exit(0)\ntime.sleep(2)"
                command=[sys.executable,'-B','-c',code]
            if case=='register_failure':
                class Broken:
                    def send(self,*a):raise OSError('fixture registration failure')
                new._registration=Broken()
                command=[sys.executable,'-B','-c','import time; time.sleep(2)']
            with new.registered_native_launches(support):
                row=support.run_child(command,out,dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),out,1,'python-only')
            event('python-child-result',row)
            if not support.process_passed(row):return 1
        for name in ('one','two'):event(name,dict(prepared_passed=True,passed=False))
        if case=='late_worker':time.sleep(.3)
        return 0
    def finish(record):
        records.append(copy.deepcopy(record))
        if case=='late_receipt' and record['passed']:time.sleep(.3)
        if case=='receipt_error' and record['passed']:raise OSError('fixture fsync failure')
        event('receipt',record)
    if case=='rss_limit':new.MAX_RSS_KIB=1  # Fixture only; production constant untouched.
    if case=='missing_metadata':
        new.metadata=lambda p:None
    if case=='old_counterexample':
        original=d.process_tree;trace=[]
        def observed_tree(pid):
            row=original(pid);trace.append(dict(wall_seconds=time.monotonic()-started,rows=row));return row
        d.process_tree=observed_tree
    code,result=d.supervise(operation,started=started,limit=limit,finish=finish)
    signal.setitimer(signal.ITIMER_REAL,0)
    event('returned',dict(code=code,result=result,actual_supervise_seconds=time.monotonic()-started,
                          children_file_exists=Path(f'/proc/{os.getpid()}/task/{os.getpid()}/children').exists(),
                          trace=trace if case=='old_counterexample' else []))
    return code


if __name__=='__main__':
    raise SystemExit(main(sys.argv[1],sys.argv[2]))
