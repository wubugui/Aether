#!/usr/bin/env python3
"""Parent-launched front-only A0/rebound A/D/A2; external errors/completeness gate."""
import argparse,fcntl,hashlib,json,os,resource,shutil,struct,subprocess,tempfile,time
from datetime import datetime,timezone
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[1];TOOLS=ROOT.parent/'tools-feiting'
PROJECT=ROOT/'candidates/round40-exclusive-20260930/project'
SCENE=PROJECT/'scenes/candidate52f/Game52f.tscn'
SCENE_SHA='201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c'
CONTRACT=P/'temporary-world-comparison-contract.json'
GLB=P.parent/'cloud-sea52h-revision-d/cloud_sea_52h_d_main_v0.glb'
GLB_SHA='0f8b70fef06f0e183b0c86138ae8e398ff699e202d0acd00f2233d8e4d9ec0aa'
SCRIPT=P/'observe52h_d_ab.gd';GODOT=TOOLS/'Godot_v4.5.1-stable_linux.x86_64'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def atomic(path,value):
    temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)
def error_lines(text):
    return [s for s in text.splitlines() if s.startswith(('ERROR:','SCRIPT ERROR:','FAIL ')) or 'leaked' in s.lower() or 'handle_crash:' in s]

ap=argparse.ArgumentParser();ap.add_argument('view',choices=['parse','front']);args=ap.parse_args()
render=args.view!='parse'
if render and not os.environ.get('DISPLAY'):raise SystemExit('Run render directions only in the existing cloud desktop terminal')
if sha(SCENE)!=SCENE_SHA or sha(GLB)!=GLB_SHA:raise SystemExit('Pinned52f scene or D source differs; no process launched')
contract=json.loads(CONTRACT.read_text());targets=contract['target_paths']
if len(targets)!=10 or len(set(targets))!=10:raise SystemExit('Exactly ten unique contracted main paths required')
lock=(TOOLS/'cloudsea52f-stage.lock').open('a')
try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('Another cloud-sea stage is active; no duplicate process launched')
out=Path(tempfile.mkdtemp(prefix=f'cloudsea52h-d-ab-{args.view}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-',dir=ROOT/'cloud-evidence'))
(TOOLS/f'feiting52h-d-ab-{args.view}-last.txt').write_text(str(out)+'\n')
inputs=[SCRIPT,Path(__file__),P/'validate52h_d_ab.py',P/'prepare_observer.py',P.parent/'cloud-sea52h-revision-d/geometry52h-d.json',P.parent/'cloud-sea52h-revision-d/cloud_sea52h_d.blend',GLB,CONTRACT,SCENE,PROJECT/'project.godot',GODOT,
 PROJECT/'tools/observe_cloudsea52f.gd',PROJECT/'tools/verify_cloudsea52e.gd',PROJECT/'tools/cloudsea52e_audit.gd',PROJECT/'tools/reflection51b_saved_audit.gd',
 PROJECT/'scenes/candidate52f/build-report-52f.json',PROJECT/'scenes/candidate52f/verified-saved-52f.json',PROJECT/'scenes/candidate51b/build-report-51b.json']
gate=json.loads((PROJECT/'scenes/candidate52f/verified-saved-52f.json').read_text())
if render:
    proof=Path(gate['process_report_path']);inputs.append(proof)
    if gate.get('audit_version')!='v3' or gate.get('runner_final_gate_passed') is not True or gate.get('candidate_sha256')!=SCENE_SHA or sha(proof)!=gate.get('process_report_sha256'):
        raise SystemExit('Fresh external-gated52f v3 proof missing or unbound; no process launched')
hashes={str(p):sha(p) for p in inputs}
atomic(out/'input-sha256.json',hashes)
for p in inputs:
    if p.suffix in ('.gd','.json'):shutil.copy2(p,out/p.name)
shutil.copy2(__file__,out/'runner.py')
shutil.copy2(P/'validate52h_d_ab.py',out/'validate52h_d_ab.py')
env=os.environ.copy()
for key,name in [('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_CONFIG_HOME','config')]:
    directory=TOOLS/'userdata'/name;directory.mkdir(parents=True,exist_ok=True);env[key]=str(directory)
command=[str(GODOT),'--path',str(PROJECT)]
if render:command+=['--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync']
else:command+=['--headless']
command+=['--script',str(SCRIPT)]
if render:command+=['--',f'--view={args.view}',f'--output-dir={out}/images']
else:command+=['--check-only']
atomic(out/'invocation.json',{'argv':command,'single_full_world':render,'parse_only':not render,'source_scene_save':False,'parent_scheduled_render_entry':render,'timeout_seconds':600 if render else 60})
start=time.monotonic();samples=[];stopped_for=None;started=datetime.now(timezone.utc).isoformat()
with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
    child=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stdout,stderr=stderr)
    (out/'child.pid').write_text(str(child.pid)+'\n');print(f'{args.view}: PID {child.pid}, {out}',flush=True)
    while True:
        try:
            status=Path(f'/proc/{child.pid}/status').read_text();row={'elapsed_s':round(time.monotonic()-start,3)}
            for line in status.splitlines():
                if line.startswith(('VmRSS:','VmHWM:')):
                    key,value=line.split(':',1);row[key+'_KiB']=int(value.split()[0])
            samples.append(row)
        except (OSError,ValueError):pass
        try:code=child.wait(timeout=1);break
        except subprocess.TimeoutExpired:pass
        logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
        # A GDScript function can abort without making Godot exit. Do not hang,
        # and never count later partial output as a successful completed study.
        hard_errors=[s for s in error_lines(logs) if s.startswith(('ERROR:','SCRIPT ERROR:')) or 'handle_crash:' in s]
        if hard_errors:stopped_for={'reason':'native_or_script_error','lines':hard_errors}
        elif time.monotonic()-start>(600 if render else 60):stopped_for={'reason':'bounded_stage_timeout'}
        if stopped_for:
            child.terminate()
            try:code=child.wait(timeout=10)
            except subprocess.TimeoutExpired:child.kill();code=child.wait()
            break
stdout=(out/'stdout.log').read_text(errors='replace');stderr=(out/'stderr.log').read_text(errors='replace')
errors=error_lines(stdout+'\n'+stderr);unchanged=all(Path(path).exists() and sha(path)==value for path,value in hashes.items())
signal=-code if code<0 else None;shell_code=128+signal if signal else code
gate_errors=[];native={};pngs=[]
if render:
    try:
        from validate52h_d_ab import validate
        gate_errors,pngs,pixel_diagnostic,requirements=validate(out,contract)
        atomic(out/'pixel-diagnostic.json',pixel_diagnostic)
        atomic(out/'runner-requirements.json',requirements)
    except (OSError,ValueError,KeyError,TypeError,IndexError,struct.error,AssertionError) as exc:
        gate_errors.append('Incomplete native/capture proof: '+str(exc))
        # Preserve any available actual A0/A pixels even if later proof is incomplete.
        try:
            from validate52h_d_ab import pixel_pair
            from PIL import Image
            import numpy as np
            a0=out/'images/1216-front-A0.png';a=out/'images/1216-front-A.png'
            if a0.exists() and a.exists():
                pair=pixel_pair(np.array(Image.open(a0).convert('RGBA')),np.array(Image.open(a).convert('RGBA')),'A0','A')
                atomic(out/'partial-A0-A-residual.json',{'pair':pair,'incomplete_run':True,'pixel_acceptance':False,'visual_acceptance':False})
        except (OSError,ValueError,KeyError,TypeError,IndexError):
            pass
final=0 if code==0 and unchanged and not errors and not gate_errors and stopped_for is None else 1
process={'view':args.view,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,
 'python_returncode':code,'shell_exit_code':shell_code,'terminating_signal':signal,'stopped_for':stopped_for,
 'child_peak_rss_KiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'memory_samples':samples,
 'frozen_inputs_unchanged':unchanged,'log_errors':errors,'runner_gate_errors':gate_errors,'runner_final_gate_passed':final==0,
 'parse_only':not render,'actual_images':pngs,'visual_acceptance':False,'hardware_gpu_acceptance':False,'complete_flight_passed':False}
atomic(out/'process-report.json',process);(out/'exit-code.txt').write_text(str(shell_code)+'\n');(out/'wrapper.exit-code.txt').write_text(str(final)+'\n')
if render:
    atomic(out/'external-gate.json',{'passed':final==0,'view':args.view,'process_report_sha256':sha(out/'process-report.json'),
      'native_report_sha256':sha(out/'images/report.json') if (out/'images/report.json').exists() else None,
      'source_scene_sha256':SCENE_SHA,'replacement_glb_sha256':GLB_SHA,'single_world_runtime_only':True,'scene_saved':False,
      'visual_acceptance':False,'failures':errors+gate_errors+([stopped_for] if stopped_for else [])})
print(json.dumps({k:process[k] for k in ['view','python_returncode','wall_seconds','child_peak_rss_KiB','frozen_inputs_unchanged','runner_gate_errors','runner_final_gate_passed']}),flush=True)
print(out,flush=True)
raise SystemExit(final)
