"""Continue the actual graded native coast with local coherent ridge/nose changes."""
from pathlib import Path
import bpy,bmesh,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];OUT=R/'captures/rightcoast_study_33a';assert not OUT.exists();OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
planpath=R/'captures/rightcoast33a-design-plan.json';plan=json.loads(planpath.read_text(encoding='utf-8'));source=R/plan['source']
assert sha(source)==plan['source_sha256'];old=json.loads((R/'captures/rightcoast33-native-intake.json').read_text(encoding='utf-8'))
shutil.copy2(__file__,OUT/'builder.py');shutil.copy2(planpath,OUT/'design-plan.json')
bpy.ops.wm.open_mainfile(filepath=str(source));checks=[]
for name,item in plan['objects'].items():
 obj=bpy.data.objects[name];assert obj.type=='MESH' and len(obj.data.vertices)==len(item['vertices'])
 assert [list(p.vertices) for p in obj.data.polygons]==old['objects'][name]['polygons']
 for i,v in enumerate(obj.data.vertices):
  assert max(abs(v.co[j]-old['objects'][name]['vertices'][i][j]) for j in range(3))<1e-7
  v.co=item['vertices'][i]
 obj.data.update();changed=set(item['changed_vertices']);materials=list(obj.data.materials)
 # Material follows newly exposed slope; original protected ground material remains.
 if name.startswith('Mainland'):
  for p in obj.data.polygons:
   if not any(i in changed for i in p.vertices) or p.center.z<=0:continue
   if p.normal.z>.89:p.material_index=3
   elif p.normal.z>.80:p.material_index=4
   else:p.material_index=1 if p.normal.x<-.2 else 0
 bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
 issues=[]
 if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold')
 if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('degenerate')
 volume=bm.calc_volume(signed=True)
 if volume<=0:issues.append('nonpositive')
 bm.to_mesh(obj.data);bm.free();obj.data.update();obj['rightcoast_revision']='33a';obj['immediate_source_blend_sha256']=plan['source_sha256']
 checks.append(dict(name=name,vertices=len(obj.data.vertices),polygons=len(obj.data.polygons),volume_m3=volume,issues=issues,changed_vertices=len(changed)))
parts=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(parts)==12
report=dict(label='33a',scope=plan['scope'],immediate_source_blend_sha256=sha(source),immediate_source_glb_sha256=sha(source.with_suffix('.glb')),parts=checks,passed=not any(p['issues'] for p in checks),production_modified=False,design_plan_sha256=sha(planpath))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'mainland_headland.blend'));assert report['passed'],checks
bpy.ops.object.select_all(action='DESELECT')
for o in parts:o.select_set(True)
bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join()
bpy.ops.export_scene.gltf(filepath=str(OUT/'mainland_headland.glb'),export_format='GLB',use_selection=True,export_apply=True)
report.update(source_sha256=sha(OUT/'mainland_headland.blend'),glb_sha256=sha(OUT/'mainland_headland.glb'))
(OUT/'native-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert sha(source)==plan['source_sha256'];print('33a native saved',json.dumps(report),flush=True)
