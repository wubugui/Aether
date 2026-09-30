from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];P=R/'captures/lantern_island_study_30c';e=json.loads((P/'geometry-evidence.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'island_c.blend'));native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    actual=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons]);assert actual==e['new'][o.name]
    bm=bmesh.new();bm.from_mesh(o.data);assert all(x.is_manifold for x in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces);volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
    native.append(dict(name=o.name,vertices=len(o.data.vertices),volume_m3=volume))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';n=e['retained_surface_vertex_count'];f=e['retained_surface_face_count']
assert e['new'][tn]['vertices'][:n]==e['old'][tn]['vertices'][:n]
assert e['new'][tn]['polygons'][:f]==[p for p in e['old'][tn]['polygons'] if all(i<n for i in p)]
assert e['new'][pn]==e['old'][pn]
for name,part in e['new'].items():
    if name not in [tn,pn]:assert part==e['old'][name]
assert len(native)==19 and 'island_c faulted bedrock' not in e['new']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(R/'reviews/round-30c-island-native-check.json').write_text(json.dumps(dict(passed=True,source_sha256=sha(P/'island_c.blend'),glb_sha256=sha(P/'island_c.glb'),source_reopened=True,all_saved_mesh_data_matches_export_evidence=True,original_terrain_top_and_path_exact=True,independent_rocks_exact=True,native_parts=native,scope='Saved native welded exterior is closed; unchanged top/path/17rocks. No all-contact, flight or visual acceptance.'),indent=2))
print('30c NATIVE REOPEN PASSED',flush=True)
