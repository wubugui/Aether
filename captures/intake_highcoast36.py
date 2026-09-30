from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[1];out=R/'reviews/36-highcoast-source-intake.json';assert not out.exists()
world=R/'scenes/world/World.tscn';text=world.read_text(encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for z in [-6,-5,-4,-3]:
    for x in [-4,-3,-2]:
        name=f'Ground_{x}_{z}'
        start=text.index(f'[node name="{name}" parent="Terrain"')
        block=text[start:text.find('\n[node ',start+1)]
        position=[float(v.strip()) for v in re.search(r'transform = Transform3D\(([^)]+)\)',block).group(1).split(',')][-3:]
        paths=[f'blender/terrain_modules/{name}.blend',f'assets/terrain/{name}.glb',f'scenes/terrain/{name}.tscn',f'assets/collision/{name}.res']
        for p in paths:assert (R/p).exists(),p
        rows.append(dict(chunk=name,world_position=position,sources={p:sha(R/p) for p in paths}))
data=dict(scope='Read-only prospective coastal highland source inventory. These12 chunks intersect a proposed design region; this is not an approved geometry footprint, occupancy clearance or completed model.',
          source_world_sha256=sha(world),design_region_xz=[[-2600,-4400],[-900,-2150]],
          geography_status='Authored continuation of same-world coast, not original game coordinate reconstruction.',chunks=rows,
          preserved_local_headland_bounds=[[-2283.037933,-2050],[-1990,-1640]],
          next_required=['Read actual saved terrain vertices and edge topology before local edit','Inventory all intersecting LandDetails, roads, settlement nodes and MultiMesh instances from World','Design highland mass, lower bays and river mouth in Blender with fixed outer interface','Update only affected mesh/collision/roads/scatter and prove seams/support','Capture same-world source-reference and oblique/flight evidence'],
          production_modified=False,geometry_created=False,full_reference_accepted=False)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(chunks=len(rows),geometry_created=False,source_inventory=str(out))))
