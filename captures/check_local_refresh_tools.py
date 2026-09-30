"""Bounded parameter/resource-retention checks; never refreshes production."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,os,shutil,subprocess,sys,uuid
R=Path('D:/test6')
D=R/'captures/local_refresh_tool_checks'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex)
D.mkdir(parents=True);(D/'.gdignore').write_text('Temporary tool checks\n')
checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(ok,name,detail=None):
    checks.append({'passed':bool(ok),'name':name,'detail':detail})
    print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def snap(base,folders=None):
    paths=[p for f in folders for p in (base/f).rglob('*')] if folders else base.rglob('*')
    return {p.relative_to(base).as_posix():sha(p) for p in paths if p.is_file() and '__pycache__' not in p.parts}
protected=snap(R,['assets','scenes','scripts','materials','blender'])
(D/'protected-before.json').write_text(json.dumps(protected,indent=2))
startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
def run(label,args,cwd=R,timeout=180):
    with (D/(label+'.log')).open('w') as out,(D/(label+'-error.log')).open('w') as err:
        p=subprocess.run([str(a) for a in args],cwd=cwd,stdout=out,stderr=err,startupinfo=startup,creationflags=subprocess.CREATE_NO_WINDOW,timeout=timeout)
    return p.returncode,(D/(label+'.log')).read_text(errors='replace')+(D/(label+'-error.log')).read_text(errors='replace')

godot=R/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
gd='''extends "res://tools/install_cliff_kit.gd"
func build() -> void:
    var kit:Array=[]
    var selected:PackedStringArray=[]
    for name in ["cliff_crown","cliff_western_slab","cliff_front_columns","cliff_central_wall","cliff_shadow_buttress","cliff_eastern_plateau"]:
        kit.append({"name":name,"position":[0,0,0]});selected.append("--asset="+name)
    kit.append({"name":"cliff_western_mesa"});kit.append({"name":"massif_frost_crown"})
    var terrain:Array=[{"name":"Ground_0_0"},{"name":"Ground_0_-1"}]
    var before:String=JSON.stringify([kit,terrain])
    var results:Array=[]
    var plan:Dictionary=plan_refresh([],kit,terrain)
    results.append({"name":"legacy full kit still includes terrain","passed":plan.ok and plan.kit.size()==8 and plan.terrain.size()==2})
    plan=plan_refresh(selected,kit,terrain)
    results.append({"name":"six selected assets do not include terrain by default","passed":plan.ok and plan.kit.size()==6 and plan.terrain.is_empty()})
    selected.append("--include-terrain");plan=plan_refresh(selected,kit,terrain)
    results.append({"name":"six selected assets plus explicit terrain","passed":plan.ok and plan.kit.size()==6 and plan.terrain==terrain})
    plan=plan_refresh(["--include-terrain"],kit,terrain)
    results.append({"name":"include-terrain without asset preserves full kit","passed":plan.ok and plan.kit.size()==8 and plan.terrain.size()==2})
    plan=plan_refresh(["--asset=cliff_crown","--asset=cliff_crown"],kit,terrain)
    results.append({"name":"duplicate selection refreshes once","passed":plan.ok and plan.kit.size()==1})
    for args in [["--asset=cliff_crown","--asset=misspelled","--include-terrain"],["--asset="],["--asset"],["--include-terrain=true"],["--include-terrian"]]:
        plan=plan_refresh(PackedStringArray(args),kit,terrain)
        results.append({"name":"reject selection before writes: "+str(args),"passed":not plan.ok and not plan.has("kit")})
    results.append({"name":"selection does not mutate original manifests","passed":before==JSON.stringify([kit,terrain])})
    var f:=FileAccess.open("REPORT",FileAccess.WRITE);f.store_string(JSON.stringify(results,"\\t"));f.close()
    quit(0 if results.all(func(r):return r.passed) else 1)
'''.replace('REPORT','res://'+(D/'godot-plan.json').relative_to(R).as_posix())
(D/'godot-plan.gd').write_text(gd)
code,logs=run('godot-plan',[godot,'--headless','--path',R,'--script',D/'godot-plan.gd'])
check(code==0 and 'SCRIPT ERROR:' not in logs and 'ERROR:' not in logs,'Godot selection function executes without errors',{'exit_code':code})
if (D/'godot-plan.json').exists():checks.extend(json.loads((D/'godot-plan.json').read_text()))
def backup_directories():
    return sorted(p.name for p in (R/'captures/edit_backups').iterdir())
backups_before=backup_directories()
code,logs=run('godot-invalid',[godot,'--headless','--path',R,'--script','tools/install_cliff_kit.gd','--','--asset=cliff_crown','--asset=misspelled','--include-terrain'])
check(code==2 and 'Unknown cliff/mountain asset: misspelled' in logs,'actual installer rejects late wrong name before backend/build',{'exit_code':code})
check(backup_directories()==backups_before,'invalid installer creates no backup directories')

spec=importlib.util.spec_from_file_location('road_builder',R/'blender/build_road_kit.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
fixture=D/'road_fixture'
for folder in ['assets/land_details','blender/road_kit','captures','scenes/world']: (fixture/folder).mkdir(parents=True,exist_ok=True)
names=['Trail_Crownreach','Trail_Amberfield','Trail_HillHamlet']
routes=[{'name':name,'width':2.4-i*.2,'points':[[12+i*15,8,20],[24+i*15,9,24],[40+i*15,10,26]]} for i,name in enumerate(names)]
entries=[{'name':name,'path':'assets/land_details/custom_'+name+'.glb','native_source':'blender/road_kit/custom_'+name+'.blend','position':[i+4,i+7,i+10],'native_note':{'keep':name}} for i,name in enumerate(names)]
reports=[{'name':name,'sentinel':'old '+name} for name in names]
for name,data in [('assets/road_routes.json',routes),('assets/road_kit.json',entries),('captures/road-authoring-validation.json',reports)]:
    (fixture/name).write_text(json.dumps(data,indent=3))
for entry in entries:
    for field in ['path','native_source']:(fixture/entry[field]).write_bytes(('untouched sentinel '+entry['name']+field).encode())
(fixture/'scenes/world/World.tscn').write_text('[gd_scene format=3]\n[node name="World" type="Node3D"]\n[node name="Routes" type="Node3D" parent="."]\nposition = Vector3(37, 11, -49)\n')
selected=[names[0],names[2]]
chosen,updates,old,previous=module.prepare_build(fixture,selected)
check([x['name'] for x in chosen]==selected,'road plan selects only requested native route names')
check(updates==[entries[0],entries[2]],'selected output paths, native sources, positions, metadata retained')
check(module.merge_entries(old,updates)==entries,'unselected manifest and order preserved')
check(len(module.prepare_build(fixture,[])[0])==3,'default road build includes all three routes')
check(module.parse_args(['--road='+names[0],'--road='+names[2]]).road==selected,'repeated road CLI parameters')
before=snap(fixture)
try:module.main(['--road='+names[0],'--road=misspelled'],root=fixture);raised=False
except ValueError as e:raised='Unknown native Godot road(s)' in str(e)
check(raised and snap(fixture)==before,'late wrong road name fails before any Blender/file operation')
# A selected output must not alias the unselected GLB and overwrite it.
collision=json.loads(json.dumps(entries));collision[0]['path']=collision[1]['path']
(fixture/'assets/road_kit.json').write_text(json.dumps(collision))
before_collision=snap(fixture)
try:module.prepare_build(fixture,selected);raised=False
except ValueError as e:raised='shared with another asset' in str(e)
check(raised and snap(fixture)==before_collision,'selected/unselected path collision rejected before writes')
(fixture/'assets/road_kit.json').write_text(json.dumps(entries,indent=3))
shutil.copy2(R/'blender/build_road_kit.py',fixture/'blender/build_road_kit.py')
(fixture/'blender/terrain_topology.py').write_text('''import numpy as np
class SurfaceSampler:
    def __init__(self):self.tiles={}
    def add(self,cx,cz,v,f):self.tiles[(cx,cz)]=(np.asarray(v)[np.asarray(f)],{(x,z):[0,1] for x in range(32) for z in range(32)})
    def height(self,x,z):return 2+.02*x+.01*z
def chunk_mesh(cx,cz):
    v=[[x,2+.02*(x+cx*768)+.01*(z+cz*768),z] for x,z in [(0,0),(768,0),(768,768),(0,768)]]
    return v,[(0,1,2),(0,2,3)]
''')
before=snap(fixture)
blender=R/'.tools/blender/blender-4.5.0-windows-x64/blender.exe'
code,logs=run('blender-selected',[blender,'--background','--factory-startup','--python-exit-code','23','--python',fixture/'blender/build_road_kit.py','--','--road='+selected[0],'--road='+selected[1]],cwd=fixture)
check(code==0 and 'Traceback (most recent call last)' not in logs,'real Blender partial build succeeds',{'exit_code':code})
after=snap(fixture)
for i in [0,2]:
    e=entries[i]
    check((fixture/e['path']).read_bytes()[:4]==b'glTF' and before[e['path']]!=after[e['path']],'selected GLB really regenerated: '+e['name'])
    check((fixture/e['native_source']).read_bytes()[:7]==b'BLENDER' and before[e['native_source']]!=after[e['native_source']],'selected native Blend really regenerated: '+e['name'])
for path in [entries[1]['path'],entries[1]['native_source'],'assets/road_routes.json','scenes/world/World.tscn','assets/road_kit.json']:
    check(before[path]==after[path],'byte-identical unselected/native authoring resource: '+path)
new_reports=json.loads((fixture/'captures/road-authoring-validation.json').read_text())
check(new_reports[1]==reports[1] and new_reports[0].get('triangles',0)>0 and new_reports[2].get('triangles',0)>0,'reports update selected entries and preserve Amberfield report')
check(not any((fixture/('assets/land_details/'+name+'.glb')).exists() for name in selected),'existing custom output paths used without creating default-path duplicates')
current=snap(R,['assets','scenes','scripts','materials','blender'])
changed=[k for k in protected.keys()|current.keys() if protected.get(k)!=current.get(k)]
check(not changed,'all production models/scenes/materials/authoring files unchanged',{'protected_files':len(protected),'changed':changed})
manifest={'passed':all(c['passed'] for c in checks),'scope':'Parameter plans and real Blender partial-export fixture, no production refresh or full game validation. Native route export remains a separate read-only Godot step.','directory':str(D),'checks':checks,'source_sha256':{p:sha(R/p) for p in ['tools/install_cliff_kit.gd','blender/build_road_kit.py']},'artifacts':{p.relative_to(D).as_posix():sha(p) for p in D.rglob('*') if p.is_file() and '__pycache__' not in p.parts}}
(D/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'passed':manifest['passed'],'checks':len(checks),'directory':str(D),'source_sha256':manifest['source_sha256']},indent=2),flush=True)
sys.exit(0 if manifest['passed'] else 1)
