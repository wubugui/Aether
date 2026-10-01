#!/usr/bin/env python3
"""Five actual source views with immutable inputs, PNG/framing and raw-log gates."""
import os,sys,json,hashlib,shutil,subprocess,tempfile,fcntl,time
from pathlib import Path
from datetime import datetime,timezone
R=Path('/workspace/scratch/a29d03198654/Aether');T=R.parent/'tools-feiting';D=Path(__file__).resolve().parent;P=R/'candidates/round40-exclusive-20260930/project'
if not os.environ.get('DISPLAY'):raise SystemExit('Parent schedules this in the actual cloud desktop renderer')
lock=(T/'cirque54v2-source-preview.lock').open('w')
try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:raise SystemExit('Cirque54v2 preview is already running')
binding=json.loads((D/'source-proof-binding.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in binding.items()),'Source/proof binding changed'
native=json.loads((D/'native-reopen-water-support-proof.json').read_text());domain=json.loads((D/'continuous-modified-domain-proof.json').read_text());selfcheck=json.loads((D/'actual-triangle-self-intersection-proof.json').read_text());zero=json.loads((D/'zero-area-candidates-diagnostic.json').read_text())
assert native['wet_surface']['oriented_geometry_float32_bytes_exact'] and native['wet_surface']['rgba_float32_bytes_exact'] and native['protected_dry_faces_exact_count']==19
assert all(r['native_reopen_geometry_and_rgba_exact_float32'] and r['boundary_edges']==r['nonmanifold_edges']==r['degenerate_faces']==0 for r in native['reopened_components'])
assert domain['all_new_modified_footprints_dry'] and domain['all_protected_regions_continuously_excluded']
assert selfcheck['all4_components_no_self_crossing'] and selfcheck['all_controls_expected'] and zero['all_candidates_strictly_disjoint']
out=Path(tempfile.mkdtemp(prefix='cirque54v2-source-preview-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=R/'cloud-evidence'));(out/'images').mkdir();(T/'cirque54v2-preview-last.txt').write_text(str(out)+'\n')
inputs=[Path(__file__),D/'preview_cirque54v2.gd',D/'source-proof-binding.json',P/'scenes/candidate53d-west/Game53dWest.tscn',P/'scenes/candidate51b/Game51b.tscn',P/'project.godot'];hashes={**binding,**{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}};(out/'input-sha256.json').write_text(json.dumps(hashes,indent=2))
for p in [Path(__file__),D/'preview_cirque54v2.gd',D/'source-proof-binding.json',D/'native-reopen-water-support-proof.json',D/'continuous-modified-domain-proof.json',D/'actual-triangle-self-intersection-proof.json',D/'zero-area-candidates-diagnostic.json']:shutil.copy2(p,out/p.name)
env=os.environ.copy();env['CIRQUE54V2_PREVIEW_OUT']=str(out/'images')
for key,tail in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:env[key]=str(T/'userdata'/tail)
cmd=[str(T/'Godot_v4.5.1-stable_linux.x86_64'),'--path',str(P),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync','--resolution','1280x960','--script',str(D/'preview_cirque54v2.gd')]
start=time.monotonic();print(out,flush=True)
with (out/'stdout.log').open('w') as stdout,(out/'stderr.log').open('w') as stderr:code=subprocess.run(cmd,cwd=R,env=env,stdout=stdout,stderr=stderr).returncode
lines=((out/'stdout.log').read_text()+'\n'+(out/'stderr.log').read_text()).splitlines();errors=[s for s in lines if s.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in s.lower()];warnings=[s for s in lines if s.startswith('WARNING:')];unexpected=[s for s in warnings if not s.startswith('WARNING: Could not set V-Sync mode, as changing V-Sync mode is not supported by the graphics driver.')];unchanged=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha for p,sha in hashes.items());gate=[]
if code!=0:gate.append('Godot process nonzero')
if errors:gate.append('Logged ERROR/SCRIPT ERROR/resource leak')
if unexpected:gate.append('Unexpected warning')
if not unchanged:gate.append('Frozen source/proof/scene input changed')
try:
 report=json.loads((out/'preview-framing.json').read_text());views=report['views']
 if not report['pass'] or len(views)!=5 or len(list((out/'images').glob('*.png')))!=5:gate.append('Incomplete five-view framing report/PNG set')
 if not all(v['png_error']==0 and v['framing_pass'] and min(v['all_vertices_frame_margins_left_top_right_bottom'])>=.07 for v in views):gate.append('PNG/framing threshold failed')
except (OSError,ValueError,KeyError,TypeError) as exc:gate.append('Missing/incomplete report: '+str(exc))
final=0 if not gate else 1
process={'godot_returncode':code,'wrapper_exit_code':final,'elapsed_seconds':time.monotonic()-start,'log_errors':errors,'warnings':warnings,'unexpected_warnings':unexpected,'frozen_inputs_unchanged':unchanged,'gate_failures':gate,'visual_acceptance':False,'integrated':False}
(out/'process-report.json').write_text(json.dumps(process,indent=2));(out/'godot.exit-code.txt').write_text(str(code)+'\n');(out/'wrapper.exit-code.txt').write_text(str(final)+'\n');(out/'exit-code.txt').write_text(str(final)+'\n');print(json.dumps({'run':str(out),**process}),flush=True);raise SystemExit(final)
