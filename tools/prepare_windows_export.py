"""Export only the playable native scene tree and its dynamic prefab library."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'assets/asset_catalog.json').read_text())
roots=['res://scenes/game.tscn']+['res://scenes/prefabs/'+item['name']+'.tscn' for item in catalog]
# Save the explicit dependency closure as well. A command-line export can use
# an old EditorFileSystem cache and otherwise omit newly authored roads or
# script preloads even though their parent scenes were selected.
selected=set();pending=roots[:]
while pending:
    resource=pending.pop()
    if resource in selected:continue
    file=ROOT/resource.removeprefix('res://')
    assert file.exists(),resource
    if file.suffix=='.json':continue  # Runtime data is included below.
    selected.add(resource)
    if file.suffix in {'.gd','.tscn','.tres','.gdshader'}:
        for dependency in re.findall(r'[\"\'](res://[^\"\']+)[\"\']',file.read_text(encoding='utf-8')):
            target=ROOT/dependency.removeprefix('res://')
            if target.is_file() and dependency not in {'res://assets/open_world.glb','res://assets/reference.jpg'}:
                pending.append(dependency)
selected=sorted(selected)
path=ROOT/'export_presets.cfg';text=path.read_text()
text=re.sub(r'export_filter="[^"]*"','export_filter="resources"',text)
text=re.sub(r'^export_files=.*\n','',text,flags=re.M)
text=text.replace('export_filter="resources"','export_filter="resources"\nexport_files=PackedStringArray('+','.join(json.dumps(s) for s in selected)+')')
runtime_json=['world_layout','water_geography','terrain_sculpt','mountain_kit','asset_catalog']
text=re.sub(r'include_filter="[^"]*"','include_filter="'+','.join('assets/'+s+'.json' for s in runtime_json)+'"',text)
text=re.sub(r'exclude_filter="[^"]*"','exclude_filter=".tools/*,blender/*,build/*,captures/*,reviews/*,reference/*,tools/*,assets/reference.jpg,assets/open_world.glb,assets/world.glb,assets/clean_plate.png"',text)
path.write_text(text)
print('WINDOWS EXPORT ROOTS',len(selected),'native scene/prefab entries; historical whole-world assets and reference excluded')
