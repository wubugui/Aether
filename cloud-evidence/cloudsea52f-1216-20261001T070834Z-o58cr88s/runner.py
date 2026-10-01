#!/usr/bin/env python3
"""One bounded52f stage per real-renderer process, with actual RSS/signal evidence."""
import fcntl, hashlib, json, os, resource, shutil, subprocess, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

repo=Path(__file__).resolve().parents[2];root=repo.parent
project=repo/'candidates/round40-exclusive-20260930/project'
stage=sys.argv[1] if len(sys.argv)>1 else ''
scripts={'build':'build_cloudsea52f.gd','audit':'verify_cloudsea52f_saved.gd','audit-v2':'verify_cloudsea52f_saved_v2.gd','audit-v3':'verify_cloudsea52f_saved_v3.gd','1128':'observe_cloudsea52f.gd','1343':'observe_cloudsea52f.gd','1216':'observe_cloudsea52f.gd','close':'observe_cloudsea52f.gd','climb':'observe_cloudsea52f.gd','under':'observe_cloudsea52f.gd'}
if stage not in scripts:raise SystemExit('Usage: python run52f.py build|audit-v3|1128|1343|1216|close|climb|under')
if not os.environ.get('DISPLAY'):raise SystemExit('Launch only in existing cloud desktop terminal; actual renderer required')
if stage=='build' and (project/'scenes/candidate52f/Game52f.tscn').exists():raise SystemExit('Saved52f exists; refusing rebuild/overwrite')
if stage!='build' and not (project/'scenes/candidate52f/build-report-52f.json').exists():raise SystemExit('Verified52f build required')
lock=(root/'tools-feiting/cloudsea52f-stage.lock').open('w')
try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('Another52f stage is active; refusing duplicate')
out=Path(tempfile.mkdtemp(prefix=f'cloudsea52f-{stage}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-',dir=repo/'cloud-evidence'))
(root/f'tools-feiting/feiting52f-{stage}-last.txt').write_text(str(out)+'\n')
inputs=[project/'tools'/scripts[stage],project/'tools/cloudsea52e_audit.gd',project/'tools/reflection51b_saved_audit.gd',project/'scenes/candidate52e/Game52e.tscn',project/'project.godot',repo/'cloud-evidence/cloudsea52f-integration-preparation/integration-manifest.json']
if stage not in ('build','audit','audit-v2','audit-v3'):inputs += [project/'tools/verify_cloudsea52e.gd',project/'scenes/candidate52f/verified-saved-52f.json']
for name in ['Game52f.tscn','build-report-52f.json']:
    p=project/'scenes/candidate52f'/name
    if p.exists():inputs.append(p)
if stage in ('audit-v2','audit-v3'):inputs.append(project/'tools/verify_cloudsea52f_saved.gd')
if stage=='audit-v3':
    for asset in json.loads((project/'scenes/candidate52f/build-report-52f.json').read_text())['source_assets']:
        inputs += [Path(asset['source']),project/asset['copy'].removeprefix('res://')]
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
(out/'input-sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')
for p in inputs:
    if p.suffix in ('.gd','.json'):shutil.copy2(p,out/p.name)
shutil.copy2(__file__,out/'runner.py')
env=os.environ.copy()
for key,tail in [('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('XDG_CONFIG_HOME','config')]:env[key]=str(root/f'tools-feiting/userdata/{tail}')
args=[f'--report-dir={out}'] if stage in ('build','audit','audit-v2','audit-v3') else [f'--subset={stage}',f'--output-dir={out}/images']
command=[str(root/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'),'--path',str(project),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync','--script',f'res://tools/{scripts[stage]}','--']+args
start=time.monotonic();samples=[];started=datetime.now(timezone.utc).isoformat()
with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:
    child=subprocess.Popen(command,cwd=repo,env=env,stdout=stdout,stderr=stderr)
    (out/'child.pid').write_text(str(child.pid)+'\n');print(f'52f{stage} PID{child.pid}: {out}',flush=True)
    while True:
        try:
            status=Path(f'/proc/{child.pid}/status').read_text();row={'elapsed_s':round(time.monotonic()-start,3)}
            for line in status.splitlines():
                if line.startswith(('VmRSS:','VmHWM:')):key,value=line.split(':',1);row[key+'_KiB']=int(value.split()[0])
            samples.append(row)
        except (OSError,ValueError):pass
        try:code=child.wait(timeout=1);break
        except subprocess.TimeoutExpired:pass
signal=-code if code<0 else None;shell_code=128+signal if signal else code
stdout=(out/'stdout.log').read_text();stderr=(out/'stderr.log').read_text()
errors=[line for line in (stdout+'\n'+stderr).splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items())
process={'stage':stage,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'wall_seconds':time.monotonic()-start,'python_returncode':code,'shell_exit_code':shell_code,'terminating_signal':signal,'child_peak_rss_KiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'memory_samples':samples,'frozen_inputs_unchanged':unchanged,'log_errors':errors,'visual_acceptance':False,'hardware_gpu_acceptance':False}
final=0 if code==0 and unchanged and not errors else 1
if stage=='audit-v3':
    gate_errors=[];native={}
    try:
        native=json.loads((out/'native-audit-report.json').read_text())
        proof_path=out/'component-and-raw-glb-proof-v3.json'
        proof=json.loads(proof_path.read_text())
        requirements={
            'provisional complete':native.get('audit_version')=='v3' and native.get('saved_native_audit_passed') is True and native.get('complete') is True and native.get('both_comparison_functions_returned') is True,
            'all native checks':all(row.get('passed') is True for row in native['checks']) and len(native['checks'])>600,
            'exact candidate/build':native['candidate_sha256']==hashes[str(project/'scenes/candidate52f/Game52f.tscn')] and native['build_report_sha256']==hashes[str(project/'scenes/candidate52f/build-report-52f.json')],
            'proof bound':Path(native['proof_path'])==proof_path and native['proof_sha256']==hashlib.sha256(proof_path.read_bytes()).hexdigest(),
            'proof complete':proof.get('passed') is True and proof.get('complete') is True and proof.get('component_function_returned') is True and proof.get('source_function_returned') is True,
            '50 components':native['component_count']==native['expected_component_count']==proof['component_count']==proof['expected_component_count']==len(proof['components'])==50 and len({r['path'] for r in proof['components']})==50,
            'all flag counts':native['recorded_flag_count']==native['expected_flag_count']==proof['recorded_flag_count']==proof['expected_flag_count']==sum(len(r['flags']) for r in proof['components']) and native['expected_flag_count']>0,
            'all native components exact':all(all(row.get(k) is True for k in ['mesh_fingerprint_exact','material_fingerprint_exact','transform_exact','all_flags_native_vs52e_exact','all_flags_json_transport_exact']) and all(f['native_vs_original_exact'] is True for f in row['flags']) for row in proof['components']),
            '6 raw source meshes':native['source_count']==proof['source_count']==len(proof['actual_glb_comparisons'])==6 and len({r['node'] for r in proof['actual_glb_comparisons']})==6,
            'all raw source geometry exact':all(row['full_resource_exact'] is True and row['all_placement_transforms_exact'] is True and all(s['all_array_bytes_exact'] is True and s['array_counts_exact'] is True and s['surface_material_exact'] is True for s in row['surfaces']) for row in proof['actual_glb_comparisons']),
        }
        gate_errors=[label for label,passed in requirements.items() if not passed]
    except (OSError,ValueError,KeyError,TypeError) as exc:gate_errors.append(f'Missing/incomplete provisional audit: {exc}')
    if gate_errors:final=1
    process['runner_audit_gate_errors']=gate_errors
    process['runner_final_gate_passed']=final==0
(out/'process-report.json').write_text(json.dumps(process,indent=2)+'\n');(out/'exit-code.txt').write_text(str(shell_code)+'\n')
if stage=='audit-v3' and final==0:
    native.update({'runner_log_gate_passed':True,'runner_final_gate_passed':True,'process_report_path':str(out/'process-report.json'),'process_report_sha256':hashlib.sha256((out/'process-report.json').read_bytes()).hexdigest(),'provisional_report_sha256':hashlib.sha256((out/'native-audit-report.json').read_bytes()).hexdigest(),'runner_version':'52f-audit-v3-final-gate'})
    gate=project/'scenes/candidate52f/verified-saved-52f.json';tmp=gate.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(native,indent=2)+'\n');tmp.replace(gate)
    shutil.copy2(gate,out/'runner-verified-saved-52f.json')
(out/'wrapper.exit-code.txt').write_text(str(final)+'\n')
print(stdout,end='');print(stderr,end='',file=sys.stderr);print(json.dumps({k:process[k] for k in ['stage','python_returncode','child_peak_rss_KiB','frozen_inputs_unchanged']}),flush=True);print(out,flush=True)
raise SystemExit(final)
