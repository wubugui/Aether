#!/usr/bin/env python3
"""Reproducible mesh-only Godot4.5.1 audit. CPU affinity <=2; 60s child ceiling."""
from pathlib import Path
import hashlib,json,os,re,shutil,signal,subprocess,tempfile,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
GODOT=ROOT.parent/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
SOURCE=ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate53d-west/Game53dWest.tscn'
HELPER=HERE.parent/'visible_geometry61.gd'
OLD=ROOT/'cloud-evidence/nearbay61-orbit-renderer-20261001T194004Z-n8gym6pm'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 out=Path(tempfile.mkdtemp(prefix='nearbay61-mesh-audit-v2-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
 scratch=Path(tempfile.mkdtemp(prefix='orbit61-mesh-fixture-',dir='/tmp'))
 print(out,flush=True)
 protected={str(p.relative_to(ROOT)):sha(p) for p in [SOURCE,*OLD.rglob('*')] if p.is_file()}
 inputs={str(p.relative_to(ROOT)):sha(p) for p in [HELPER,HERE/'fixture.gd',Path(__file__)]}
 text=SOURCE.read_text()
 blocks={m[1]:m[0] for m in re.finditer(r'^\[sub_resource type="ArrayMesh" id="([^"]+)"\]\n.*?(?=^\[|\Z)',text,re.M|re.S)}
 pairs={name:re.search(r'^shadow_mesh = SubResource\("([^"]+)"\)',block,re.M)[1] for name,block in blocks.items() if '\nshadow_mesh = ' in block}
 assert len(pairs)==403
 wanted=set(pairs)|set(pairs.values())
 selected=[]; extraction=[]
 for name,block in blocks.items():
  if name not in wanted:continue
  stripped,n=re.subn(r'^"material": (?:SubResource|ExtResource)\("[^"\n]+"\),?\n','',block,flags=re.M)
  # Exactly this one known non-geometric property is removed; every other byte stays.
  assert 'ExtResource(' not in stripped
  selected.append(stripped)
  extraction.append({'id':name,'original_block_sha256':hashlib.sha256(block.encode()).hexdigest(),'fixture_block_sha256':hashlib.sha256(stripped.encode()).hexdigest(),'material_reference_lines_removed':n})
 fixture='[gd_resource type="Resource" load_steps=%d format=3]\n\n'%(len(selected)+1)+''.join(selected)+'[resource]\nmetadata/source_meshes = {\n'+',\n'.join(json.dumps(name)+': SubResource('+json.dumps(name)+')' for name in pairs)+'\n}\n'
 fixture_path=scratch/'meshes.tres';fixture_path.write_text(fixture)
 (scratch/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Mesh-only orbit61 fixture"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n[threading]\nworker_pool/max_threads=2\n')
 for p in [HELPER,HERE/'fixture.gd',Path(__file__)]:shutil.copy2(p,out/p.name)
 env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2')
 for key,sub in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
  (scratch/sub).mkdir();env[key]=str(scratch/sub)
 cpus=sorted(os.sched_getaffinity(0))[:2]
 command=[str(GODOT),'--headless','--path',str(scratch),'--audio-driver','Dummy','--script',str(HERE/'fixture.gd'),'--',str(HELPER),str(fixture_path),str(out/'result.json')]
 start=time.monotonic();timed_out=False
 with (out/'stdout.log').open('wb') as stdout,(out/'stderr.log').open('wb') as stderr:
  child=subprocess.Popen(command,env=env,stdout=stdout,stderr=stderr,start_new_session=True,preexec_fn=lambda:os.sched_setaffinity(0,cpus))
  while True:
   pid,status,usage=os.wait4(child.pid,os.WNOHANG)
   if pid:code=os.waitstatus_to_exitcode(status);child.returncode=code;break
   if time.monotonic()-start>60:
    timed_out=True;os.killpg(child.pid,signal.SIGKILL);pid,status,usage=os.wait4(child.pid,0);code=os.waitstatus_to_exitcode(status);child.returncode=code;break
   time.sleep(.05)
 elapsed=time.monotonic()-start
 after={name:sha(ROOT/name) for name in protected}
 errors=[line for p in [out/'stdout.log',out/'stderr.log'] for line in p.read_text(errors='replace').splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
 result=json.loads((out/'result.json').read_text()) if (out/'result.json').exists() else {}
 report={'version':'orbit61-mesh-audit-v2','command':command,'cpu_affinity':cpus,'wall_limit_seconds':60,'wall_seconds':elapsed,'returncode':code,'max_rss_kib':usage.ru_maxrss,'timeout':timed_out,'godot_sha256':sha(GODOT),'inputs':inputs,'source_scene_sha256':sha(SOURCE),'fixture_sha256':sha(fixture_path),'fixture_bytes':fixture_path.stat().st_size,'extraction':extraction,'protected_inputs_count':len(protected),'protected_inputs_unchanged':protected==after,'logged_errors':errors,'passed':code==0 and not timed_out and not errors and protected==after and result.get('passed',False),'no_world_loaded':True,'no_images':True,'orbit_runtime_passed':False,'temporary_geometry_location':str(fixture_path),'temporary_geometry_not_for_commit':True}
 (out/'wrapper-report.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['passed','returncode','wall_seconds','max_rss_kib','logged_errors','protected_inputs_unchanged']},indent=2))
 return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
