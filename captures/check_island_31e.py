from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];P=R/'captures/lantern_island_study_31e';e=json.loads((P/'geometry-evidence.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(P/'shoulder_operands.blend'))
authoring=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(authoring)==len(e['additions'])
for spec in e['additions']:
    matches=[o for o in authoring if o.name.startswith(spec['name'])];assert len(matches)==1;o=matches[0]
    actual=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons]);assert actual==spec['actual_operand_geometry']
    bm=bmesh.new();bm.from_mesh(o.data);assert all(x.is_manifold for x in bm.edges) and bm.calc_volume(signed=True)>0;bm.free()
bpy.ops.wm.open_mainfile(filepath=str(P/'island_c.blend'));native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    actual=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons]);assert actual==e['new'][o.name]
    bm=bmesh.new();bm.from_mesh(o.data);assert all(x.is_manifold for x in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces);volume=bm.calc_volume(signed=True);assert volume>0;bm.free()
    if o.name!='island_c grass and exposed rock terrain':assert actual==e['old'][o.name]
    native.append(dict(name=o.name,vertices=len(o.data.vertices),volume_m3=volume))
assert len(native)==19
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(R/'reviews/round-31e-island-native-check.json').write_text(json.dumps(dict(passed=True,source_sha256=sha(P/'island_c.blend'),glb_sha256=sha(P/'island_c.glb'),shoulder_operands_sha256=sha(P/'shoulder_operands.blend'),authoring_editable_solids_reopened=len(authoring),source_reopened=True,all_saved_mesh_data_matches_export_evidence=True,path_and_17_rocks_exact=True,native_parts=native,scope='Saved union exterior is closed. Three historical shoulder operands reopened in separate native scene. Same17rocks/path; occupied support, exposed shape and actual runtime require independent checks.'),indent=2))
print('31e NATIVE REOPEN PASSED',flush=True)
