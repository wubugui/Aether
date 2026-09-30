"""Reopen saved source and compare actual protected terrain support."""
from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'captures/lantern_island_study_29b'
def capture(p):
    bpy.ops.wm.open_mainfile(filepath=str(p));result={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(o.data)
        result[o.name]={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons],'closed':all(e.is_manifold for e in bm.edges),'nonzero_faces':all(f.calc_area()>1e-9 for f in bm.faces),'volume_m3':bm.calc_volume(signed=True)};bm.free()
    return result
old=capture(R/'captures/lantern_island_study_29a/island_c.blend');new=capture(OUT/'island_c.blend');plan=json.loads((OUT/'terrain-plan.json').read_text())
path='island_c terrain fitted keeper paths';terrain='island_c grass and exposed rock terrain';core='island_c faulted bedrock'
assert old[path]==new[path]
assert old[terrain]['polygons']==new[terrain]['polygons']
for i in plan['protected_vertex_indices']:assert old[terrain]['vertices'][i]==new[terrain]['vertices'][i]
for i in plan['protected_face_indices']:assert old[terrain]['materials'][i]==new[terrain]['materials'][i]
n=plan['top_vertex_count'];assert new[core]['vertices'][72:]==new[terrain]['vertices'][n:]
assert new[core]['vertices'][:36]==old[core]['vertices'][:36]
assert new[core]['polygons']==old[core]['polygons']
changed=sum(a!=b for a,b in zip(old[terrain]['vertices'][:n],new[terrain]['vertices'][:n]));assert changed==plan['changed_top_vertices']
assert len(new)==20
for name,d in new.items():assert d['closed'] and d['nonzero_faces'] and d['volume_m3']>0,name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':True,'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'source_reopened':True,'path_unchanged':True,'protected_terrain_vertices_unchanged':True,'protected_terrain_faces':len(plan['protected_face_indices']),'changed_top_vertices':changed,'core_top_equals_terrain_underside':True,'core_bottom_waterline_unchanged':True,'parts':len(new),'native_parts':[{'name':name,**{k:v for k,v in d.items() if k not in ['vertices','polygons','materials']}} for name,d in new.items()],'scope':'Actual saved source reopened. Closed/positive solids and exact protected support do not prove whole-asset no intersections, full traversal, or visual fidelity.'}
(R/'reviews/round-29b-island-native-check.json').write_text(json.dumps(report,indent=2));print('29b SAVED SOURCE CHECK PASSED',flush=True)
