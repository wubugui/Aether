"""Apply reviewed independent assets and regenerate only their dependents."""
from pathlib import Path
import sys,json,shutil,hashlib,subprocess,datetime
root=Path('D:/test6');backup=root/'captures/asset_backups/round-10a-before-10d'
run=root/'captures/round-10l-source-integration'
assert not run.exists(),'Keep every integration attempt and its logs'
run.mkdir();log={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stages':[],'passed':False}
def save():(run/'manifest.json').write_text(json.dumps(log,indent=2))
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def preserve(relative):
    src=root/relative;dst=backup/relative
    if src.exists() and not dst.exists():dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
def stage(name,args,timeout=240):
    command=[str(x) for x in args]
    with (run/(name+'.stdout.log')).open('w') as out,(run/(name+'.stderr.log')).open('w') as err:
        result=subprocess.run(command,cwd=root,stdout=out,stderr=err,startupinfo=startup,timeout=timeout)
    record={'name':name,'command':command,'exit_code':result.returncode};log['stages'].append(record);save()
    assert result.returncode==0,name+' failed; see preserved logs'
    error=(run/(name+'.stderr.log')).read_text(errors='replace')
    assert not any(x in error for x in ['SCRIPT ERROR:','Traceback (most recent call last)','AssertionError']),name+' emitted a script error'
    print('Completed',name,flush=True)
try:
    for relative,sha in json.loads((backup/'files.json').read_text()).items():
        assert digest(root/relative)==sha,'Source changed since 10a backup: '+relative
    report=json.loads((root/'captures/round-10l-plateau-geometry.json').read_text())
    assert report['passed'] and digest(root/'captures/cliff_sections_10l_eastern_plateau.glb')==report['glb_sha256']
    for relative in ['assets/road_kit.json','assets/road_routes.json','captures/road-authoring-validation.json',
        'assets/models/cliff_eastern_plateau.glb','blender/cliff_kit/cliff_eastern_plateau.blend',
        'scenes/prefabs/cliff_eastern_plateau.tscn','assets/collision/cliff_eastern_plateau.res','assets/meshes/cliff_eastern_plateau.res']:
        preserve(relative)
    road_manifest=json.loads((root/'assets/road_kit.json').read_text())
    for item in road_manifest:
        preserve(item['path']);preserve(item['native_source'])
    untouched={}
    for item in road_manifest:
        if item['name'] not in ['Trail_Crownreach','Trail_HillHamlet']:
            for path in [item['path'],item['native_source']]:untouched[path]=digest(root/path)
    draft=root/'captures/round-10d-integration-draft'
    shutil.copy2(draft/'cliff_sections.py',root/'blender/cliff_sections.py')
    shutil.copy2(draft/'terrain_sculpt.json',root/'assets/terrain_sculpt.json')
    for suffix,target in [('glb','assets/models/cliff_eastern_plateau.glb'),('blend','blender/cliff_kit/cliff_eastern_plateau.blend')]:
        shutil.copy2(root/'captures'/('cliff_sections_10l_eastern_plateau.'+suffix),root/target)
    native_report=json.loads((root/'captures/round-10l-plateau-seating.json').read_text())
    kit=json.loads((root/'assets/cliff_kit.json').read_text())
    item=next(x for x in kit if x['name']=='cliff_eastern_plateau')
    item.update(vertices=native_report['vertices'],faces=native_report['faces'],volume_m3=native_report['volume_m3'],
        modeling_method='Native plateau with preserved vertex paint and a retopologized terrain-contact band')
    (root/'assets/cliff_kit.json').write_text(json.dumps(kit,indent=2))
    blender=root/'.tools/blender/blender-4.5.0-windows-x64/blender.exe'
    godot=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
    stage('model-five-cliffs',[blender,'-b','--python-exit-code','1','--python','blender/model_cliff_kit.py','--',
        'cliff_crown','cliff_western_slab','cliff_front_columns','cliff_central_wall','cliff_shadow_buttress'])
    stage('model-two-ground-tiles',[blender,'-b','--python-exit-code','1','--python','blender/rebuild_terrain_modules.py','--','0,-1','0,0'])
    updates=json.loads((root/'assets/terrain_updates.json').read_text());assert {i['name'] for i in updates}=={'Ground_0_0','Ground_0_-1'}
    stage('export-saved-native-routes',[godot,'--path',root,'--script','tools/export_road_routes.gd'])
    stage('model-two-roads',[blender,'-b','--python-exit-code','1','--python','blender/build_road_kit.py','--',
        '--road=Trail_Crownreach','--road=Trail_HillHamlet'])
    for path,sha in untouched.items():assert digest(root/path)==sha,'Unselected road changed: '+path
    stage('import-assets',[godot,'--headless','--editor','--path',root,'--quit'],timeout=300)
    stage('refresh-selected-prefabs',[godot,'--path',root,'--script','tools/install_cliff_kit.gd','--','--include-terrain',
        '--asset=cliff_crown','--asset=cliff_western_slab','--asset=cliff_front_columns','--asset=cliff_central_wall',
        '--asset=cliff_shadow_buttress','--asset=cliff_eastern_plateau'])
    log.update(passed=True,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),unchanged_road_files=untouched)
    save();print('10l assets integrated; game/road/visual acceptance still requires the next scoped run.',flush=True)
except Exception as error:
    log['error']=str(error);save();raise
