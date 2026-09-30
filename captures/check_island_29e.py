"""Reopen saved source and compare actual protected terrain support."""
from pathlib import Path
import bpy,bmesh,json,hashlib,struct
R=Path(__file__).resolve().parents[1];OUT=R/'captures/lantern_island_study_29e'
def capture(p):
    bpy.ops.wm.open_mainfile(filepath=str(p));result={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(o.data)
        result[o.name]={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons],'closed':all(e.is_manifold for e in bm.edges),'nonzero_faces':all(f.calc_area()>1e-9 for f in bm.faces),'volume_m3':bm.calc_volume(signed=True)};bm.free()
    return result
old=capture(R/'captures/lantern_island_study_29d/island_c.blend');new=capture(OUT/'island_c.blend');plan=json.loads((OUT/'terrain-plan.json').read_text())
path='island_c terrain fitted keeper paths';terrain='island_c grass and exposed rock terrain';core='island_c faulted bedrock'
assert old[path]['polygons']==new[path]['polygons']
assert all(a[:2]==b[:2] for a,b in zip(old[path]['vertices'],new[path]['vertices']))
assert old[terrain]['polygons']==new[terrain]['polygons']
for i in plan['protected_vertex_indices']:assert old[terrain]['vertices'][i]==new[terrain]['vertices'][i]
for i in plan['protected_face_indices']:assert old[terrain]['materials'][i]==new[terrain]['materials'][i]
n=plan['top_vertex_count'];assert new[core]['vertices'][54:]==new[terrain]['vertices'][n:]
assert new[core]['vertices'][:36]==old[core]['vertices'][:36]
assert len(new[core]['vertices'])==54+n
changed_exact=sum(a!=b for a,b in zip(old[terrain]['vertices'][:n],new[terrain]['vertices'][:n]))
changed=sum(max(abs(x-y) for x,y in zip(a,b))>1e-5 for a,b in zip(old[terrain]['vertices'][:n],new[terrain]['vertices'][:n]));assert changed==plan['changed_top_vertices']
f32=lambda x:struct.unpack('f',struct.pack('f',x))[0]
assert new[terrain]['vertices']==[[f32(x) for x in p] for p in plan['terrain_vertices']]
assert len(new)==20
for name,d in new.items():assert d['closed'] and d['nonzero_faces'] and d['volume_m3']>0,name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':True,'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'source_reopened':True,'path_xy_topology_preserved_and_height_rebuilt':True,'protected_terrain_vertices_unchanged':True,'protected_terrain_faces':len(plan['protected_face_indices']),'changed_top_vertices':changed,'core_top_equals_terrain_underside':True,'core_bottom_waterline_unchanged':True,'parts':len(new),'native_parts':[{'name':name,**{k:v for k,v in d.items() if k not in ['vertices','polygons','materials']}} for name,d in new.items()],'scope':'Actual saved source reopened. Closed/positive solids and exact protected support do not prove whole-asset no intersections, full traversal, or visual fidelity.'}
(R/'reviews/round-29e-island-native-check.json').write_text(json.dumps(report,indent=2));print('29e SAVED SOURCE CHECK PASSED',flush=True)
