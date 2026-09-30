"""Reopen actual saved Blender assets and check retained support geometry."""
from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'captures/lantern_island_study_29a'
def capture(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    data={}
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        data[obj.name]={'vertices':[list(v.co) for v in obj.data.vertices],'polygons':[list(p.vertices) for p in obj.data.polygons],'materials':[p.material_index for p in obj.data.polygons],'closed':all(e.is_manifold for e in bm.edges),'nonzero_faces':all(f.calc_area()>1e-9 for f in bm.faces),'volume_m3':bm.calc_volume(signed=True)}
        bm.free()
    return data
old=capture(R/'captures/lantern_islands_study_20l/island_c.blend');new=capture(OUT/'island_c.blend')
for name in ['island_c grass and exposed rock terrain','island_c terrain fitted keeper paths']:
    assert old[name]==new[name],name
name='island_c faulted bedrock'
assert old[name]['vertices'][72:]==new[name]['vertices'][72:]
assert old[name]['vertices'][:36]==new[name]['vertices'][:36]
assert old[name]['polygons']==new[name]['polygons']
assert len(new)==27
for name,d in new.items():assert d['closed'] and d['nonzero_faces'] and d['volume_m3']>0,name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':True,'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'source_reopened':True,'retained_terrain_and_path_exact':True,'retained_core_top_support_vertices':True,'retained_core_bottom_and_waterline_vertices':True,'retained_core_polygon_topology':True,'parts':len(new),'native_parts':[{k:v for k,v in d.items() if k not in ['vertices','polygons','materials']}|{'name':name,'vertices':len(d['vertices']),'polygons':len(d['polygons'])} for name,d in new.items()],'scope':'Actual saved BLEND reopening and exact source geometry comparisons. Runtime collision/placement and reference fidelity require GPU/world evidence; no whole-island intersection-free assertion.'}
(R/'reviews/round-29a-island-native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('29a REOPENED NATIVE CHECK PASS '+str(len(new)),flush=True)
