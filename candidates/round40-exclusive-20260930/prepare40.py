from pathlib import Path
import json, re, hashlib

base=Path(__file__).resolve().parent
project=base/'project'
for old,new in [('game39.gd','game40.gd'),('environment39.gd','environment40.gd')]:
    text=(project/'scripts'/old).read_text(encoding='utf8')
    text=text.replace('SceneEnvironment39','SceneEnvironment40').replace('scene39_progress','round40_progress').replace('第39轮候选','第40轮候选')
    if new=='environment40.gd':
        text=text.replace('reference_views39.json','reference_views40.json')
        text=text.replace('var cabin := "SkyRegion39/Cabin" in str(lamp.get_path())','var cabin := "SkyRegion39/Cabin" in str(lamp.get_path()) or "CarriageLamp40" in str(lamp.name)')
    (project/'scripts'/new).write_text(text,encoding='utf8')
plan=json.loads((project/'assets/reference_views39.json').read_text(encoding='utf8'))
for entry in plan:
    if entry['env'].get('water_night',0)>.5:
        # True engine ambient and directional light; shader colours unchanged.
        entry['env']['ambient_color']=[.24,.36,.64]
        entry['env']['ambient_energy']=.50
        entry['env']['sun_color']=[.56,.68,1.0]
        entry['env']['sun_energy']=.48
(project/'assets/reference_views40.json').write_text(json.dumps(plan,indent=2),encoding='utf8')
config=(project/'project.godot').read_text(encoding='utf8').replace('res://scenes/game.tscn','res://scenes/candidate40/Game40.tscn')
(project/'project.godot').write_text(config,encoding='utf8')
print(json.dumps({e['ref']:{'camera':e['camera'],'env':e['env']} for e in plan if e['ref'] in ['1342','1274','1278']},indent=2))
# Audit candidate independence: source references use res://; no junctions.
foreign=[]
for path in project.rglob('*'):
    if path.is_file() and path.suffix in ['.gd','.gdshader','.tscn','.tres','.godot']:
        text=path.read_text(encoding='utf8',errors='replace')
        for line in text.splitlines():
            if re.search(r'[A-Z]:[/\\]',line) and ('load(' in line or 'path=' in line or 'open(' in line):
                foreign.append({'path':str(path.relative_to(project)), 'line':line[:180]})
(base/'evidence/independence-audit.json').write_text(json.dumps({'external_resource_references':foreign},indent=2),encoding='utf8')
print('foreign live resource references',len(foreign))
