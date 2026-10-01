#!/usr/bin/env python3
"""Parent-launched single-variable exact-resource cache diagnostic; no D asset load."""
import argparse,fcntl,hashlib,json,os,resource,shutil,struct,subprocess,tempfile,time
from datetime import datetime,timezone
from pathlib import Path

P=Path(__file__).resolve().parent;ROOT=P.parents[2];TOOLS=ROOT.parent/'tools-feiting'
PROJECT=ROOT/'candidates/round40-exclusive-20260930/project'
SCENE=PROJECT/'scenes/candidate52f/Game52f.tscn'
SCENE_SHA='201f667747406b1414a298a6b5433ac1550d8b447dff8f6cb6823d94d2acbd7c'
CONTRACT=P.parent/'revision-d-combination/temporary-world-comparison-contract.json'
GLB=P.parent/'revision-d-combination/cloud_sea_52g_d_main_only.glb'
GLB_SHA='a399fac8726ab341757a7249d17773e14a28002337eb86ae5e159d9436438624'
SCRIPT=P/'observe52g_cache.gd';GODOT=TOOLS/'Godot_v4.5.1-stable_linux.x86_64'
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
out=Path(tempfile.mkdtemp(prefix=f'cloudsea52g-cache-diagnostic-v2-{args.view}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-',dir=ROOT/'cloud-evidence'))
(TOOLS/f'feiting52g-cache-diagnostic-v2-{args.view}-last.txt').write_text(str(out)+'\n')
inputs=[SCRIPT,P.parent/'runtime-d-ab/observe52g_d_ab.gd',Path(__file__),GLB,CONTRACT,SCENE,PROJECT/'project.godot',GODOT,
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
env=os.environ.copy()
for key,name in [('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_CONFIG_HOME','config')]:
    directory=TOOLS/'userdata'/name;directory.mkdir(parents=True,exist_ok=True);env[key]=str(directory)
command=[str(GODOT),'--path',str(PROJECT)]
if render:command+=['--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync']
else:command+=['--headless']
command+=['--script',str(SCRIPT)]
if render:command+=['--',f'--view={args.view}',f'--output-dir={out}/images']
else:command+=['--check-only']
atomic(out/'invocation.json',{'argv':command,'single_full_world':render,'parse_only':not render,'source_scene_save':False,'no_gui_launched_by_source_worker':True,'timeout_seconds':600 if render else 60})
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
        native=json.loads((out/'images/report.json').read_text())
        phases=native['phase_rows'];restored=native['restore_rows'];captures=native['captures']
        requirements={
          'complete diagnostic':native.get('diagnostic_complete') is True and native.get('diagnostic_checks_passed') is True,
          'ten exact target paths':sorted(native['target_paths'])==sorted(targets),
          'only rebind intervention returned':native['intervention_returned'] is True,
          'all checks passed':bool(native['checks']) and all(x.get('passed') is True for x in native['checks']),
          'four phases full native and viewport exact':len(phases)==4 and [p['phase'] for p in phases]==['A0','A1','R0','R1'] and all(p['native_full_exact'] is True and p['viewport_exact'] is True and p['dimensions_contract_exact'] is True and all(p[k] is True for k in ['requested_size_exact','content_config_exact','actual_readback_size_exact','texture_metadata_formula_exact','projection_aspect_exact']) and p['texture_metadata_dimensions']==[831,468] and p['metadata_expected_from_engine_formula']==[831,468] and p['actual_dimensions']==[1179,664] and p['requested_dimensions']==[1180,664] and p['expected_dimensions_from_fixed_project']==[1179,664] and not p['stored_differences'] and not p['runtime_differences'] for p in phases),
          'ten equivalent clones':len(native['clone_rows'])==10 and sorted(r['path'] for r in native['clone_rows'])==sorted(targets) and all(all(r[k] is True for k in ['distinct_resource_and_rid','all_geometry_native_bytes_exact','surface_material_identities_exact']) for r in native['clone_rows']),
          'ten rebinds and restores':len(native['rebind_rows'])==10 and sorted(r['path'] for r in native['rebind_rows'])==sorted(targets) and all(all(r[k] is True for k in ['clone_was_bound','original_identity_restored','all_components_untouched_exact','flags_exact','active_material_identity_exact']) for r in native['rebind_rows']),
          'ten component proofs':len(restored)==10 and sorted(r['path'] for r in restored)==sorted(targets) and all(all(r[k] is True for k in ['all_components_exact','mesh_resource_identity_restored','flags_typed_exact','active_material_identity_exact']) and len(r['components'])==6 and all(c['exact'] is True and c['before_bytes']==c['restored_bytes'] for c in r['components']) for r in restored),
          'original resources retained':native['original_resources_kept']==10,
          'three original active materials':len(native['live_cloud_bindings'])==4 and all(r['old']==75 and r['new']==50 and r['material_count']==3 and len(r['rows'])==125 for r in native['live_cloud_bindings']),
          'four captures':len(captures)==4 and [r['phase'] for r in captures]==['A0','A1','R0','R1'],
          'fixed projection and lighting':all(captures[0][key]==row[key] for row in captures[1:] for key in ['camera_transform','camera_fov','camera_near','camera_far','camera_keep_aspect','camera_projection_columns','environment','reflection_sync_count','world_chunk_count','world_core_count']),
          'scope and non-acceptance explicit':native['single_full_world'] is True and all(native[k] is False for k in ['scene_saved','geometry_shape_changed','material_changed','lighting_changed','D_source_loaded','visual_acceptance','hardware_gpu_acceptance','complete_flight_passed','shadow_root_cause_proven']),
          'matching fixed scene':native['scene_sha256']==SCENE_SHA,
        }
        from PIL import Image
        import numpy as np
        rgba={}
        for row in captures:
            path=Path(row['path']);raw=path.read_bytes();dims=struct.unpack('>II',raw[16:24])
            pngs.append({'name':path.name,'bytes':len(raw),'dimensions':list(dims),'sha256':sha(path)})
            if raw[:8]!=b'\x89PNG\r\n\x1a\n':gate_errors.append('PNG signature mismatch: '+path.name)
            if dims!=(1179,664) or list(dims)!=row['size']:gate_errors.append('Actual PNG dimensions violate fixed project/viewport contract: '+path.name)
            if sha(path)!=row['sha256']:gate_errors.append('PNG hash mismatch: '+path.name)
            rgba[row['phase']]=np.array(Image.open(path).convert('RGBA'))
        pairs=[]
        for a,b in [('A0','A1'),('A0','R0'),('R0','R1'),('A0','R1')]:
            d=np.abs(rgba[a].astype(np.int16)-rgba[b].astype(np.int16));m=np.any(d,axis=2);ys,xs=np.where(m)
            pairs.append({'a':a,'b':b,'rgba_exact':not bool(m.any()),'changed_pixels':int(m.sum()),'max_channel_difference':int(d.max()),'absolute_channel_sum':int(d.sum()),'bbox':None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],'first_20_pixels':[{'x':int(x),'y':int(y),'a':rgba[a][y,x].tolist(),'b':rgba[b][y,x].tolist()} for y,x in list(zip(ys,xs))[:20]]})
        atomic(out/'pixel-diagnostic.json',{'pairs':pairs,'pixel_acceptance':False,'root_cause_proven':False})
        requirements['native/external equality reports agree']=native['baseline_repeat_pixels_exact']==pairs[0]['rgba_exact'] and native['A0_R0_pixels_exact']==pairs[1]['rgba_exact'] and native['restored_repeat_pixels_exact']==pairs[2]['rgba_exact']
        expected=[f'1216-front-{phase}.png' for phase in ['A0','A1','R0','R1']]
        requirements['four actual PNG files']=sorted(p.name for p in (out/'images').glob('*.png'))==sorted(expected)
        gate_errors += [label for label,ok in requirements.items() if not ok]
    except (OSError,ValueError,KeyError,TypeError,IndexError,struct.error) as exc:gate_errors.append('Incomplete native/capture proof: '+str(exc))
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
      'source_scene_sha256':SCENE_SHA,'D_source_loaded':False,'single_world_runtime_only':True,'scene_saved':False,
      'visual_acceptance':False,'diagnostic_only':True,'pixel_acceptance':False,'shadow_root_cause_proven':False,'failures':errors+gate_errors+([stopped_for] if stopped_for else [])})
print(json.dumps({k:process[k] for k in ['view','python_returncode','wall_seconds','child_peak_rss_KiB','frozen_inputs_unchanged','runner_gate_errors','runner_final_gate_passed']}),flush=True)
print(out,flush=True)
raise SystemExit(final)
