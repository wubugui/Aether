"""Run the cliff refresh GPU fixture with a protected-production hash audit."""
from pathlib import Path
import datetime, hashlib, json, os, shutil, subprocess, sys, uuid

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'captures/cliff_refresh_regressions' / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex)
RUN.mkdir(parents=True)
(RUN/'.gdignore').write_text('Temporary GPU fixture resources\n')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def protected():
    paths = []
    for folder in ['assets', 'scenes', 'scripts', 'materials', 'blender']:
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    old = ROOT/'captures/validation_runs/10a-cliff-edit-20260905T180959Z-d5293d6da65f4bf9bd3f633c321d3c0c'
    paths.extend(p for p in old.rglob('*') if p.is_file())
    return {p.relative_to(ROOT).as_posix():digest(p) for p in sorted(paths)}

before = protected()
(RUN/'protected-before.json').write_text(json.dumps(before, indent=2))
tool_files = ['tools/install_cliff_kit.gd','tools/cliff_refresh.gd','tools/verify_cliff_refresh.gd','tools/run_cliff_refresh_regression.py','tools/assemble_world.gd','scripts/scatter_group.gd']
tool_hashes = {name:digest(ROOT/name) for name in tool_files}
for name in tool_files:
    target = RUN/'source'/name; target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(ROOT/name,target)
command = [str(ROOT/'.tools/godot/Godot_v4.5.1-stable_win64.exe'), '--path', str(ROOT), '--script', 'tools/verify_cliff_refresh.gd', '--', '--fixture-directory=res://'+RUN.relative_to(ROOT).as_posix()]
startup = None
flags = 0
if os.name == 'nt':
    startup = subprocess.STARTUPINFO(); startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW; startup.wShowWindow = 0
    flags = subprocess.CREATE_NO_WINDOW
error = None
try:
    with (RUN/'gpu.log').open('w') as out, (RUN/'gpu-error.log').open('w') as err:
        process = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err, startupinfo=startup, creationflags=flags, timeout=180)
    code = process.returncode
except Exception as exc:
    code = -1; error = str(exc)
after = protected()
changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
changed_tools = [name for name in tool_files if digest(ROOT/name) != tool_hashes[name]]
gpu = json.loads((RUN/'gpu-report.json').read_text()) if (RUN/'gpu-report.json').exists() else None
logs = (RUN/'gpu.log').read_text() + (RUN/'gpu-error.log').read_text()
passed = code == 0 and gpu is not None and gpu.get('passed') is True and not changed and not changed_tools and 'SCRIPT ERROR:' not in logs and 'ERROR:' not in logs
manifest = {'passed':passed,'run_directory':str(RUN),'command':command,'exit_code':code,'error':error,'protected_files':len(before),'changed_production_or_10a_evidence':changed,'tool_sha256':tool_hashes,'changed_tools':changed_tools,'checks':len(gpu['checks']) if gpu else 0,'artifacts':{p.relative_to(RUN).as_posix():digest(p) for p in RUN.rglob('*') if p.is_file()}}
(RUN/'manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(manifest, indent=2), flush=True)
sys.exit(0 if passed else 1)
