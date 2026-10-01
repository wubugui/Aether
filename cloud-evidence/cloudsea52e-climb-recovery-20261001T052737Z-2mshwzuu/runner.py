#!/usr/bin/env python3
"""Launch exactly one bounded graphical subset, preserving signal and actual peakRSS."""
import fcntl
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
root = repo.parent
project = repo/'candidates/round40-exclusive-20260930/project'
subset = sys.argv[1] if len(sys.argv)>1 else ''
if subset not in ('close','climb'):
    raise SystemExit('Usage: python run_remaining52e.py close|climb')
if not os.environ.get('DISPLAY'):
    raise SystemExit('Actual renderer required: launch only from existing cloud desktop terminal')
lock = (root/'tools-feiting/cloudsea52e-remaining.lock').open('w')
try:
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
    raise SystemExit('A52e remaining subset already runs; refusing duplicate')
out = Path(tempfile.mkdtemp(prefix=f'cloudsea52e-{subset}-recovery-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-',dir=repo/'cloud-evidence'))
(root/f'tools-feiting/feiting52e-{subset}-recovery-last.txt').write_text(str(out)+'\n')
inputs=[project/'tools/observe_cloudsea52e_remaining.gd',project/'tools/verify_cloudsea52e.gd',project/'tools/cloudsea52e_audit.gd',project/'tools/reflection51b_saved_audit.gd',project/'scenes/candidate52e/Game52e.tscn',project/'scenes/candidate52e/build-report-52e.json',project/'project.godot',repo/'cloud-evidence/cloudsea52e-paired-20261001T050129Z-geTptG/51b/report.json']
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
(out/'input-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
for source in inputs[:4]+inputs[5:6]:shutil.copy2(source,out/source.name)
shutil.copy2(__file__,out/'runner.py')
env=os.environ.copy()
for key,tail in [('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_CONFIG_HOME','config')]:env[key]=str(root/f'tools-feiting/userdata/{tail}')
command=[str(root/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'),'--path',str(project),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync','--script','res://tools/observe_cloudsea52e_remaining.gd','--',f'--subset={subset}',f'--output-dir={out}/images']
started=datetime.now(timezone.utc).isoformat();start=time.monotonic();samples=[]
with (out/'observer.stdout.log').open('w') as stdout,(out/'observer.stderr.log').open('w') as stderr:
    child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,cwd=repo)
    (out/'child.pid').write_text(str(child.pid)+'\n')
    print(f'{subset}52e recovery started PID{child.pid}: {out}',flush=True)
    while True:
        try:
            status=Path(f'/proc/{child.pid}/status').read_text()
            row={'elapsed_seconds':round(time.monotonic()-start,3)}
            for line in status.splitlines():
                if line.startswith(('VmRSS:','VmHWM:')):
                    key,value=line.split(':',1);row[key+'_KiB']=int(value.split()[0])
            samples.append(row)
        except (OSError,ValueError):pass
        try:code=child.wait(timeout=1);break
        except subprocess.TimeoutExpired:pass
usage=resource.getrusage(resource.RUSAGE_CHILDREN)
signal=-code if code<0 else None
shell_code=128+signal if signal else code
(out/'observer.exit-code.txt').write_text(str(shell_code)+'\n')
stderr=(out/'observer.stderr.log').read_text();stdout=(out/'observer.stdout.log').read_text()
errors=[line for line in (stdout+'\n'+stderr).splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
run={'subset':subset,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'python_returncode':code,'shell_exit_code':shell_code,'terminating_signal':signal,'child_peak_rss_KiB':usage.ru_maxrss,'ru_maxrss_units':'KiB on this Linux host; RUSAGE_CHILDREN, one child in this runner','observed_process_memory_samples':samples,'all_frozen_input_files_unchanged':unchanged,'log_errors':errors,'single_saved_candidate_only':True,'baseline_scene_loaded':False,'full_native_graph_snapshot_created':False,'original_pair_runtime_metadata_complete':False,'original_exit137_cause':'unknown; no OOM claim','visual_acceptance':False,'hardware_gpu_acceptance':False}
(out/'process-report.json').write_text(json.dumps(run,indent=2)+'\n')
final=0 if code==0 and not errors and unchanged else 1
(out/'wrapper.exit-code.txt').write_text(str(final)+'\n')
print(stdout,end='');print(stderr,end='',file=sys.stderr)
print(json.dumps({k:run[k] for k in ('subset','python_returncode','terminating_signal','child_peak_rss_KiB','all_frozen_input_files_unchanged')}),flush=True)
print(f'Evidence: {out}',flush=True)
raise SystemExit(final)
