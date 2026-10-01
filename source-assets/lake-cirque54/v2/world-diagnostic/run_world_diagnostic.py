#!/usr/bin/env python3
"""Two original-camera world views of actual cirque54v2 root replacement."""
import os,sys,json,time,selectors,subprocess,hashlib,shutil,tempfile,fcntl,re
from pathlib import Path
from datetime import datetime,timezone
R=Path('/workspace/scratch/a29d03198654/Aether');T=R.parent/'tools-feiting';D=R/'source-assets/lake-cirque54/v2/world-diagnostic';P=R/'candidates/round40-exclusive-20260930/project'
if not os.environ.get('DISPLAY'):raise SystemExit('Actual cloud desktop renderer required; parent schedules this probe')
lock=(T/'cirque54v2-world.lock').open('w')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('A cirque54phase probe is already active')
out=Path(tempfile.mkdtemp(prefix='cirque54v2-world-diagnostic-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=R/'cloud-evidence'))
(T/'cirque54v2-world-diagnostic-last.txt').write_text(str(out)+'\n');(out/'images').mkdir()
F=R/'source-assets/lake-cirque54/v2/final-source'
binding=json.loads((F/'source-proof-binding.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in binding.items()),'Frozen source/proof binding differs'
assert json.loads((D/'isolated-replacement-array-proof.json').read_text())['passed'],'Isolated native array replacement failed'
source_preview=R/'cloud-evidence/cirque54v2-source-preview-20261001T084921Z-8w68fr6m/process-report.json'
assert json.loads(source_preview.read_text())['wrapper_exit_code']==0,'Actual clean source five-view run required'
inputs=[Path(__file__),D/'diagnose_cirque54v2_world.gd',D/'native-mesh-encoding.json',D/'probe_native_mesh_encoding.gd',D/'probe_replacement_arrays.gd',D/'isolated-replacement-array-proof.json',F/'source-proof-binding.json',F/'surface-and-wet-ledger.json',R/'source-assets/lake-cirque54/v2/native-authority/cirque-native-authority.json',source_preview,P/'scenes/candidate53d-west/Game53dWest.tscn',P/'scenes/candidate51b/Game51b.tscn',P/'project.godot']+list(map(Path,binding))
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs};(out/'input-sha256.json').write_text(json.dumps(hashes,indent=2))
shutil.copy2(__file__,out/'runner.py');shutil.copy2(D/'diagnose_cirque54v2_world.gd',out/'diagnose_cirque54v2_world.gd')
env=os.environ.copy();env['CIRQUE54_WORLD_OUT']=str(out/'images')
for key,tail in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:env[key]=str(T/'userdata'/tail)
command=[str(T/'Godot_v4.5.1-stable_linux.x86_64'),'--path',str(P),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync','--resolution','1280x960','--script',str(D/'diagnose_cirque54v2_world.gd')]
start=time.monotonic();proc=subprocess.Popen(command,cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
(out/'child.pid').write_text(str(proc.pid));print(out,flush=True)
sel=selectors.DefaultSelector();buffers={};files={};phases={'stdout':'process_start','stderr':'process_start'};errors=[];warnings=[];events=[]
for stream in ['stdout','stderr']:
 pipe=getattr(proc,stream);os.set_blocking(pipe.fileno(),False);sel.register(pipe,selectors.EVENT_READ,stream);buffers[stream]=b'';files[stream]=(out/(stream+'.log')).open('wb')
combined=(out/'ordered-stream-events.jsonl').open('w')
def record(stream,line):
 text=line.decode('utf8',errors='replace').rstrip('\r\n');files[stream].write(line);files[stream].flush()
 if text.startswith('CIRQUE54_PHASE '):
  try:phases[stream]=json.loads(text.split(' ',1)[1])['phase']
  except (ValueError,KeyError):pass
 row={'received_elapsed_s':time.monotonic()-start,'stream':stream,'stream_phase':phases[stream],'line':text};combined.write(json.dumps(row)+'\n');combined.flush();events.append(row)
 if re.match(r'^(ERROR:|SCRIPT ERROR:)',text) or 'leaked' in text.lower():errors.append(row)
 if text.startswith('WARNING:'):warnings.append(row)
while sel.get_map():
 for key,_ in sel.select(timeout=1):
  stream=key.data;data=os.read(key.fileobj.fileno(),65536)
  if not data:
   if buffers[stream]:record(stream,buffers[stream]);buffers[stream]=b''
   sel.unregister(key.fileobj);continue
  buffers[stream]+=data
  while b'\n' in buffers[stream]:
   line,buffers[stream]=buffers[stream].split(b'\n',1);record(stream,line+b'\n')
code=proc.wait();combined.close()
for f in files.values():f.close()
unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items());gate=[]
if code!=0:gate.append('Godot process returned nonzero')
if errors:gate.append('Godot ERROR/SCRIPT ERROR/resource leak in raw logs')
if not unchanged:gate.append('Frozen input changed')
unexpected=[r for r in warnings if not r['line'].startswith('WARNING: Could not set V-Sync mode, as changing V-Sync mode is not supported by the graphics driver.')]
if unexpected:gate.append('Unexpected warning')
try:
 report=json.loads((out/'diagnostic-report.json').read_text());caps=report['captures']
 if report['failures'] or len(caps)!=2 or any(c['error']!=0 for c in caps):gate.append('Incomplete/failed two-view world report')
 if not report['material_checks_all_passed']:gate.append('Material binding/RID check failed')
 for key in ['scatter_unchanged','all_collision_unchanged','saved53west_file_unchanged','all_west_meshes_collision_material_bindings_unchanged','all_other_mesh_geometry_bindings_unchanged','original_root_other_properties_preserved','root_mesh_actually_replaced','original_raw_native_authority_exact','all_runtime_payload_raw_positions_native_encoded_rgba_exact']:
  if not report[key]:gate.append(key)
 if len(list((out/'images').glob('*.png')))!=2:gate.append('Expected2actual PNGs')
 if not report['wet_and_protected_native_faces']['oriented_native_world_geometry_rgba_exact']:gate.append('Wet/protected native faces differ')
except (OSError,ValueError,KeyError,TypeError) as exc:gate.append('Missing/incomplete diagnostic report: '+str(exc))
if phases['stderr']!='quit.requested':gate.append('Cleanup/quit phase not reached')
final=0 if not gate else 1
process={'scope':'Two fixed original cameras of temporary cirque54v2 root ArrayMesh replacement plus3snow leaves. Full collision/scatter retain53west. No integration or visual acceptance.','child_returncode':code,'wrapper_exit_code':final,'elapsed_seconds':time.monotonic()-start,'frozen_inputs_unchanged':unchanged,'log_errors':errors,'warnings':warnings,'unexpected_warnings':unexpected,'gate_failures':gate,'stream_end_phases':phases,'phase_attribution':'Within-stream stderr markers bracket GLES errors. Cross-stream reception timestamps are evidence of receipt order, not assumed render causality.','visual_acceptance':False,'integrated':False}
(out/'process-report.json').write_text(json.dumps(process,indent=2));(out/'godot.exit-code.txt').write_text(str(code)+'\n');(out/'wrapper.exit-code.txt').write_text(str(final)+'\n');(out/'exit-code.txt').write_text(str(final)+'\n')
print(json.dumps({'run':str(out),'child_returncode':code,'wrapper_exit_code':final,'errors':len(errors),'gate_failures':gate}),flush=True)
raise SystemExit(final)
