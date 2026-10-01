import os,json,subprocess,tempfile,hashlib,time,shutil
from pathlib import Path
from datetime import datetime,timezone
R=Path('/workspace/scratch/a29d03198654/Aether');T=R.parent/'tools-feiting';P=R/'candidates/round40-exclusive-20260930/project'
assert os.environ.get('DISPLAY'),'Actual desktop renderer required'
out=Path(tempfile.mkdtemp(prefix='observation55-scope-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-'),dir=R/'cloud-evidence'))
(T/'observation55-scope-last.txt').write_text(str(out))
env=os.environ.copy();env['OBSERVATION55_OUT']=str(out)
for k,v in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:env[k]=str(T/'userdata'/v)
inputs=[P/'scenes/candidate53d-west/Game53dWest.tscn',P/'scenes/candidate55-observation/Game55Observation.tscn',P/'scripts/game55_observation.gd',P/'assets/observation55/lake_observation_poses.json',P/'project.godot']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes={str(p):sha(p) for p in inputs};(out/'input-sha256.json').write_text(json.dumps(hashes,indent=2))
cmd=[str(T/'Godot_v4.5.1-stable_linux.x86_64'),'--path',str(P),'--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync','--script',str(R/'source-assets/observation55/verify_inherited_scope55.gd')]
shutil.copy2(Path(__file__),out/'runner.py');shutil.copy2(R/'source-assets/observation55/verify_inherited_scope55.gd',out/'verify_inherited_scope55.gd')
start=time.monotonic()
with (out/'stdout.log').open('w') as a,(out/'stderr.log').open('w') as b:
 c=subprocess.run(cmd,env=env,stdout=a,stderr=b,timeout=180).returncode
logs=(out/'stdout.log').read_text()+'\n'+(out/'stderr.log').read_text()
errors=[s for s in logs.splitlines() if s.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in s.lower()]
try:report=json.loads((out/'scope-report.json').read_text())
except (OSError,ValueError):report={}
unchanged=all(sha(Path(p))==h for p,h in hashes.items())
ok=c==0 and not errors and unchanged and report.get('passed_provisional') is True
(out/'process-report.json').write_text(json.dumps({'child_exit':c,'errors':errors,'inputs_unchanged':unchanged,'passed':ok,'elapsed':time.monotonic()-start},indent=2));(out/'exit-code.txt').write_text('0' if ok else '1')
print(out,ok,flush=True)
raise SystemExit(0 if ok else 1)
