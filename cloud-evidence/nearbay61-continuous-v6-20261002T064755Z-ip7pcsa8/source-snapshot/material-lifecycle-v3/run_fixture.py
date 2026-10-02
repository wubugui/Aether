#!/usr/bin/env python3
"""Explicit --run only: synthetic material/queue fixture, Godot4.5.1, CPU2, <=60s."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,signal,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GODOT=ROOT.parent/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
EXPECTED_GODOT='db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
OLD=[ROOT/'cloud-evidence'/name for name in ['nearbay61-orbit-renderer-20261001T194004Z-n8gym6pm','nearbay61-orbit-renderer-20261002T023336Z-nuh5s3o7']]
SOURCES=[HERE.parent/'visible_geometry61.gd',HERE.parent/'fixture_lifecycle61.gd',HERE.parent/'verify_orbit61.gd',HERE/'fixture.gd',Path(__file__)]
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def manifest(paths):return {str(p.relative_to(ROOT)):sha(p) for p in paths}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--run',action='store_true');args=parser.parse_args()
 if not args.run:
  print('Source preparation only. Use --run after the coordinated CPU window is authorized.');return 0
 assert sha(GODOT)==EXPECTED_GODOT
 out=Path(tempfile.mkdtemp(prefix='nearbay61-material-lifecycle-v3-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
 scratch=Path(tempfile.mkdtemp(prefix='orbit61-material-lifecycle-',dir='/tmp'))
 print(out,flush=True)
 original_paths=[Path(p) for p in json.loads((OLD[0]/'input-sha256.json').read_text())]
 protected_paths=sorted(set(original_paths+[p for old in OLD for p in old.rglob('*') if p.is_file()]))
 protected=manifest(protected_paths);inputs=manifest(SOURCES)
 for path in SOURCES:shutil.copy2(path,out/path.name)
 (scratch/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Orbit61 material and lifecycle fixture"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n[threading]\nworker_pool/max_threads=2\n')
 env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
 for key,sub in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
  (scratch/sub).mkdir();env[key]=str(scratch/sub)
 cpus=sorted(os.sched_getaffinity(0))[:2]
 command=[str(GODOT),'--headless','--path',str(scratch),'--audio-driver','Dummy','--script',str(HERE/'fixture.gd'),'--',str(out/'result.json')]
 started=time.monotonic();timed_out=False
 with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
  child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=lambda:os.sched_setaffinity(0,cpus))
  while True:
   pid,status,usage=os.wait4(child.pid,os.WNOHANG)
   if pid:code=os.waitstatus_to_exitcode(status);child.returncode=code;break
   if time.monotonic()-started>59:
    timed_out=True;os.killpg(child.pid,signal.SIGKILL);pid,status,usage=os.wait4(child.pid,0);code=os.waitstatus_to_exitcode(status);child.returncode=code;break
   time.sleep(.025)
 elapsed=time.monotonic()-started
 errors=[line for p in [out/'stdout.log',out/'stderr.log'] for line in p.read_text(errors='replace').splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
 result=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
 unchanged=protected==manifest(protected_paths) and inputs==manifest(SOURCES)
 report={'version':'orbit61-material-lifecycle-v3','command':command,'cpu_affinity':cpus,'watchdog_seconds':59,'maximum_requested_seconds':60,'wall_seconds':elapsed,'returncode':code,'max_rss_kib':usage.ru_maxrss,'timeout':timed_out,'godot_sha256':EXPECTED_GODOT,'inputs':inputs,'protected_input_count':len(protected),'protected_input_manifest_sha256':hashlib.sha256(json.dumps(protected,sort_keys=True).encode()).hexdigest(),'inputs_unchanged':unchanged,'logged_errors':errors,'passed':code==0 and elapsed<=60 and not timed_out and not errors and unchanged and result.get('passed',False),'world_loaded':False,'images':0,'orbit_runtime_passed':False}
 (out/'wrapper-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
