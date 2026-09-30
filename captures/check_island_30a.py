from pathlib import Path
import bpy,bmesh,json,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'captures/lantern_island_study_30a';e=json.loads((OUT/'geometry-evidence.json').read_text());plan=json.loads((OUT/'proportion-plan.json').read_text());bpy.ops.wm.open_mainfile(filepath=str(OUT/'island_c.blend'))
native=[]
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 actual={'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]};assert actual==e['new'][o.name],o.name
 bm=bmesh.new();bm.from_mesh(o.data);assert all(x.is_manifold for x in bm.edges);assert all(f.calc_area()>1e-10 for f in bm.faces);vol=bm.calc_volume(signed=True);assert vol>0;bm.free();native.append({'name':o.name,'volume_m3':vol,'vertices':len(o.data.vertices)})
t=e['new']['island_c grass and exposed rock terrain'];c=e['new']['island_c faulted bedrock'];n=plan['top_vertex_count'];assert c['vertices'][54:]==t['vertices'][n:];assert len(native)==20
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();(R/'reviews/round-30a-island-native-check.json').write_text(json.dumps({'passed':True,'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'source_reopened':True,'all_saved_mesh_data_matches_export_evidence':True,'core_terrain_interface_exact':True,'native_parts':native,'scope':'Actual saved editable Blender source. Site/path geometric coverage independently checked; runtime assembly, collisions and visual proportions remain to verify.'},indent=2));print('30a NATIVE REOPEN PASSED',flush=True)
