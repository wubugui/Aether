#!/usr/bin/env python3
"""Explicit --run: native input-unit fixture, Godot4.5.1, CPU2, <=20s; no world."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GODOT=ROOT.parent/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
EXPECTED_GODOT='db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
OLD=[ROOT/'cloud-evidence'/name for name in ['nearbay61-orbit-renderer-20261001T194004Z-n8gym6pm','nearbay61-orbit-renderer-20261002T023336Z-nuh5s3o7','nearbay61-orbit-renderer-20261002T033202Z-i141mgll','nearbay61-orbit-renderer-20261002T040614Z-kyawbpny']]
SOURCES=[HERE.parent/'native_mouse61.gd',HERE.parent/'verify_orbit61.gd',HERE.parent/'run_orbit61.py',HERE/'fixture.gd',Path(__file__),HERE/'README.md']
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def manifest(paths):return {str(p.relative_to(ROOT)):sha(p) for p in paths}
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');args=parser.parse_args()
 if not args.run:
  print('Source preparation only. Use --run in the parent-coordinated CPU window.');return 0
 assert sha(GODOT)==EXPECTED_GODOT
 out=Path(tempfile.mkdtemp(prefix='nearbay61-input-units-v5-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
 scratch=Path(tempfile.mkdtemp(prefix='orbit61-input-units-',dir='/tmp'))
 print(out,flush=True)
 original_paths=[Path(p) for p in json.loads((OLD[0]/'input-sha256.json').read_text())]
 protected_paths=sorted(set(original_paths+[p for old in OLD for p in old.rglob('*') if p.is_file()]))
 protected=manifest(protected_paths);inputs=manifest(SOURCES)
 write(out/'protected-before.json',protected);write(out/'sources-before.json',inputs)
 for path in SOURCES:shutil.copy2(path,out/path.name)
 (scratch/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Orbit61 native input coordinate fixture"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n[threading]\nworker_pool/max_threads=2\n')
 shutil.copy2(scratch/'project.godot',out/'synthetic-project.godot')
 env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1')
 for key,sub in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
  (scratch/sub).mkdir();env[key]=str(scratch/sub)
 cpus=sorted(os.sched_getaffinity(0))[:2]
 command=[str(GODOT),'--headless','--path',str(scratch),'--audio-driver','Dummy','--script',str(HERE/'fixture.gd'),'--',str(out/'result.json')]
 started=time.monotonic();timed_out=False;external_signal=None
 with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
  child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=lambda:os.sched_setaffinity(0,cpus))
  write(out/'process.json',{'status':'running','pid':child.pid,'command':command})
  def stop(signum,_frame):
   nonlocal external_signal
   external_signal=signum
   try:os.killpg(child.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  previous={sig:signal.signal(sig,stop) for sig in (signal.SIGTERM,signal.SIGINT)}
  try:
   while True:
    pid,status,usage=os.wait4(child.pid,os.WNOHANG)
    if pid:code=os.waitstatus_to_exitcode(status);child.returncode=code;break
    if time.monotonic()-started>19:
     timed_out=True;os.killpg(child.pid,signal.SIGKILL);pid,status,usage=os.wait4(child.pid,0);code=os.waitstatus_to_exitcode(status);child.returncode=code;break
    time.sleep(.025)
  finally:
   for sig,handler in previous.items():signal.signal(sig,handler)
 elapsed=time.monotonic()-started
 errors=[line for p in [out/'stdout.log',out/'stderr.log'] for line in p.read_text(errors='replace').splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
 result=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
 protected_after=manifest(protected_paths);inputs_after=manifest(SOURCES)
 write(out/'protected-after.json',protected_after);write(out/'sources-after.json',inputs_after)
 unchanged=protected==protected_after and inputs==inputs_after
 report={'version':'orbit61-native-input-units-v5','status':'finished','command':command,'cpu_affinity':cpus,'watchdog_seconds':19,'maximum_requested_seconds':20,'wall_seconds':elapsed,'returncode':code,'max_rss_kib':usage.ru_maxrss,'timeout':timed_out,'wrapper_received_signal':external_signal,'godot_sha256':EXPECTED_GODOT,'inputs':inputs,'protected_input_count':len(protected),'inputs_unchanged':unchanged,'logged_errors':errors,'passed':code==0 and elapsed<=20 and not timed_out and external_signal is None and not errors and unchanged and result.get('passed',False),'world_loaded':False,'images':0,'orbit_runtime_passed':False}
 write(out/'process.json',report);write(out/'wrapper-report.json',report)
 (out/'exit-code.txt').write_text('0\n' if report['passed'] else '1\n')
 print(json.dumps(report,indent=2));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
