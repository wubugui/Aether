"""Complete the revised terrain cage's four-cell dependency footprint."""
from pathlib import Path
import json,hashlib,shutil,subprocess,datetime
root=Path('D:/test6');run=root/'captures/round-10l-neighbor-integration'
assert not run.exists();run.mkdir();backup=run/'before'
log={'passed':False,'stages':[],'before':{},'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
def save():(run/'manifest.json').write_text(json.dumps(log,indent=2))
for relative in ['assets/terrain_updates.json','scenes/world/World.tscn','assets/asset_catalog.json']+[f'{folder}/Ground_{cx}_{cz}.{ext}' for cx,cz in [(-1,-1),(-1,0)] for folder,ext in [('assets/terrain','glb'),('blender/terrain_modules','blend'),('assets/collision','res'),('assets/meshes','res'),('scenes/terrain','tscn')]]:
 src=root/relative;dst=backup/relative;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 log['before'][relative]=hashlib.sha256(src.read_bytes()).hexdigest()
save()
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
blender=root/'.tools/blender/blender-4.5.0-windows-x64/blender.exe';godot=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
commands=[('model-neighbor-tiles',[blender,'-b','--python-exit-code','1','--python','blender/rebuild_terrain_modules.py','--','-1,-1','-1,0']),
 ('import-assets',[godot,'--headless','--editor','--path',root,'--quit']),
 ('refresh-neighbor-terrain',[godot,'--path',root,'--script','tools/install_cliff_kit.gd','--','--asset=cliff_crown','--include-terrain'])]
try:
 for name,args in commands:
  with (run/(name+'.stdout.log')).open('w') as out,(run/(name+'.stderr.log')).open('w') as err:
   result=subprocess.run([str(x) for x in args],cwd=root,stdout=out,stderr=err,startupinfo=startup,timeout=300)
  log['stages'].append({'name':name,'exit_code':result.returncode});save()
  text=(run/(name+'.stdout.log')).read_text(errors='replace')+(run/(name+'.stderr.log')).read_text(errors='replace')
  assert result.returncode==0 and not any(s in text for s in ['SCRIPT ERROR:','ERROR:','Traceback (most recent call last)','AssertionError']),name+' failed'
  print('Completed '+name,flush=True)
 log.update(passed=True,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());save()
except Exception as error:log['error']=str(error);save();raise
