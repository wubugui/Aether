from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];src=R/'captures/village_grading_study_26b/mainland_headland.blend';before=hashlib.sha256(src.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(src));objects={};stats=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);vol=bm.calc_volume(signed=True);bad=sum(not e.is_manifold for e in bm.edges);bm.free();vs=[list(o.matrix_world@v.co) for v in o.data.vertices];o.data.calc_loop_triangles();ts=[list(t.vertices) for t in o.data.loop_triangles]
 objects[o.name]=dict(vertices=vs,triangles=ts,polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons],material_names=[m.name for m in o.data.materials],matrix_world=[list(row) for row in o.matrix_world])
 stats.append(dict(name=o.name,vertices=len(vs),triangles=len(ts),polygons=len(o.data.polygons),volume_m3=vol,nonmanifold_edges=bad,bounds=[[min(v[k] for v in vs) for k in range(3)],[max(v[k] for v in vs) for k in range(3)]]))
assert before==hashlib.sha256(src.read_bytes()).hexdigest()
out=dict(scope='Read-only current26b right coast native source intake for next main-reference depth/rock-coast stage. No new model, no old23g reset, no world or paving mutation.',source=str(src.relative_to(R)),source_sha256=before,objects=objects,statistics=stats,scene_properties={k:str(v) for k,v in bpy.context.scene.items()})
p=R/'captures/rightcoast33-native-intake.json';assert not p.exists();p.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(stats,indent=2),flush=True)
