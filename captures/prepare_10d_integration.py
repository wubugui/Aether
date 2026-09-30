"""Make reviewable source drafts and a 10a backup; no production writes."""
from pathlib import Path
import json,shutil,hashlib
root=Path('D:/test6');draft=root/'captures/round-10d-integration-draft'
draft.mkdir(exist_ok=True)
source=(root/'captures/cliff_sections_10d.py').read_text()
start=source.index('# Study-only terrain cage edit')
end=source.index('\nF=941/',start)
source=source[:start]+source[end:]
source=source.replace('# Two concave channels survive as aligned edges through all wall sections.', '# Small depth offsets turn the three broad wall blocks away from a flat extrusion.')
(draft/'cliff_sections.py').write_text(source)
cages=json.loads((root/'assets/terrain_sculpt.json').read_text())
def smooth(a,b,x):
    t=max(0.,min(1.,(x-a)/(b-a)));return t*t*(3-2*t)
for cage in cages:
    if cage['name']!='Crown Escarpment foothills':continue
    for p in cage['points']:
        x,y,z=p
        southwest=smooth(-5,20,x)*(1-smooth(90,130,x))*smooth(-80,-20,z)*(1-smooth(65,110,z))
        central=smooth(90,115,x)*(1-smooth(170,205,x))*smooth(-90,-40,z)*(1-smooth(60,110,z))
        p[1]=y-13*max(southwest,central)
    cage['purpose']='Continuous foothills and local seated foundations below independently assembled cliff prefabs'
(draft/'terrain_sculpt.json').write_text(json.dumps(cages,indent=2))
check=(root/'captures/check_10c_study.py').read_text().replace('10c','10d')
(root/'captures/check_10d_study.py').write_text(check)
backup=root/'captures/asset_backups/round-10a-before-10d'
assert not backup.exists(),'Do not overwrite a prior baseline'
files=['blender/cliff_sections.py','blender/model_cliff_kit.py','assets/terrain_sculpt.json','assets/cliff_kit.json','assets/terrain_updates.json','assets/asset_catalog.json','scenes/world/World.tscn']
for kind in ['crown','western_slab','front_columns','shadow_buttress','central_wall']:
    files.extend([f'assets/models/cliff_{kind}.glb',f'blender/cliff_kit/cliff_{kind}.blend',f'scenes/prefabs/cliff_{kind}.tscn',f'assets/collision/cliff_{kind}.res',f'assets/meshes/cliff_{kind}.res'])
for name in ['Ground_0_0','Ground_0_-1']:
    files.extend([f'assets/terrain/{name}.glb',f'blender/terrain_modules/{name}.blend',f'scenes/terrain/{name}.tscn',f'assets/collision/{name}.res',f'assets/meshes/{name}.res'])
manifest={}
for path in files:
    source=root/path
    if not source.exists():continue
    target=backup/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
    manifest[path]=hashlib.sha256(source.read_bytes()).hexdigest()
(backup/'files.json').write_text(json.dumps(manifest,indent=2))
print('Prepared two source drafts and',len(manifest),'verified-source backups. No production files changed.')
