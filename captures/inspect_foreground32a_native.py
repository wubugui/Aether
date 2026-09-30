from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];src=R/'captures/lantern_islands_study_20l/island_a.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));objects={};stats=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 vs=[list(v.co) for v in o.data.vertices];ps=[list(p.vertices) for p in o.data.polygons]
 objects[o.name]=dict(vertices=vs,polygons=ps,materials=[p.material_index for p in o.data.polygons],material_names=[m.name for m in o.data.materials],matrix_world=[list(row) for row in o.matrix_world])
 bm=bmesh.new();bm.from_mesh(o.data);bounds=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]
 stats.append(dict(name=o.name,vertices=len(vs),faces=len(ps),bounds=bounds,volume_m3=bm.calc_volume(signed=True),closed=all(e.is_manifold for e in bm.edges)));bm.free()
out=dict(source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),objects=objects,statistics=stats,scene_properties={k:str(v) for k,v in bpy.context.scene.items()},scope='Read actual20lA native mesh coordinates and topology for32a foreground reconstruction. No source/model mutation or repeated world generation.')
p=R/'captures/foreground32a-native-intake.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2),flush=True)
