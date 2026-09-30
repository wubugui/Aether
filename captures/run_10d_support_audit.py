"""Read-only GPU support audit; protects all production authoring/runtime files."""
import datetime,hashlib,json,subprocess,os,sys
from pathlib import Path
R=Path('D:/test6')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot():
    return {p.relative_to(R).as_posix():sha(p) for folder in ['assets','scenes','scripts','materials','blender'] for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
before=snapshot()
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
command=[str(R/'.tools/godot/Godot_v4.5.1-stable_win64.exe'),'--path',str(R),'--script','captures/audit_10d_support.gd']
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
with (R/'captures/round-10d-readonly-support.log').open('w') as out,(R/'captures/round-10d-readonly-support-error.log').open('w') as err:
    result=subprocess.run(command,cwd=R,stdout=out,stderr=err,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW,timeout=300)
after=snapshot()
changed=[p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)]
manifest={'started_utc':start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'command':command,'protected_files':len(before),'changed_production_files':changed,'script_sha256':sha(R/'captures/audit_10d_support.gd'),'report_sha256':sha(R/'captures/round-10d-readonly-support.json') if (R/'captures/round-10d-readonly-support.json').exists() else None,'stderr_bytes':(R/'captures/round-10d-readonly-support-error.log').stat().st_size}
(R/'captures/round-10d-readonly-support-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest,indent=2),flush=True)
sys.exit(0 if not changed and result.returncode==0 and manifest['stderr_bytes']==0 else 1)
