from pathlib import Path
import json,hashlib,numpy as np
from shapely.geometry import Point,shape,box
R=Path(__file__).resolve().parents[1];read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(R/'captures/rightcoast33b-design-plan.json');check=read(R/'captures/rightcoast_study_33b/native-check.json');original=read(R/'captures/rightcoast33-native-intake.json')
source=R/'captures/rightcoast_study_33b/mainland_headland.blend';assert sha(source)==check['source_sha256']
floor=box(-28,-7,-14,10);occupied=shape(read(R/'reviews/round-33-occupied-regions.json')['hard_occupied_house_and_paving_union']);assert floor.distance(occupied)>8
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
objects={};before={};changed_total=0
for name,entry in old['objects'].items():
 v=np.array(entry['vertices'],dtype=np.float32).astype(float);new=v.copy();locked=set(entry['frozen_vertices']);ids=[]
 for i,(x,y,z) in enumerate(v):
  if i in locked or z<=0:continue
  distance=floor.distance(Point(x,y));w=1-smooth(distance/11)
  if w<=0:continue
  # A low broad rock working shore, with an inclined landward transition.
  target=1.6+max(0,y-10)*.16
  new[i,2]=z+w*(min(z,target)-z)
  if abs(new[i,2]-z)>1e-6:ids.append(i)
 changed_total+=len(ids);objects[name]=dict(vertices=new.tolist(),frozen_vertices=entry['frozen_vertices'],changed_vertices=ids,max_displacement_m=float(np.max(np.linalg.norm(new-v,axis=1))))
 before[name]=dict(vertices=v.tolist(),polygons=original['objects'][name]['polygons'])
plan=dict(label='33c',scope='Continue actual33b coast; form one broad low rock working shore at inner bay. Retain complete frozen actual house/paving support faces, all XY/topology, original source bottom and mainland seam. No full visual/reference acceptance.',source=str(source.relative_to(R)),source_sha256=check['source_sha256'],origin=old['origin'],objects=objects,expected_source_objects=before,working_shore=dict(bounds_blender_xy=list(floor.bounds),target_height_m=1.6,outer_blend_m=11,actual_occupied_distance_m=floor.distance(occupied)),basis='33b',changed_vertex_count=changed_total,actual_occupied_report_sha256=sha(R/'reviews/round-33-occupied-regions.json'))
p=R/'captures/rightcoast33c-design-plan.json';assert not p.exists();p.write_text(json.dumps(plan,indent=2),encoding='utf-8')
s=(R/'blender/model_rightcoast_33b.py').read_text(encoding='utf-8').replace('33b','33c')
s=s.replace("old=json.loads((R/'captures/rightcoast33-native-intake.json').read_text(encoding='utf-8'))","old={'objects':plan['expected_source_objects']}")
s=s.replace("if p.normal.z>.89:p.material_index=3","if -28<=p.center.x<=-14 and -7<=p.center.y<=10:p.material_index=1\n+   elif p.normal.z>.89:p.material_index=3".replace('\n+','\n'))
p=R/'blender/model_rightcoast_33c.py';assert not p.exists();p.write_text(s,encoding='utf-8')
s=(R/'tools/render_rightcoast_33b.py').read_text(encoding='utf-8').replace('33b','33c')
# This edit's immediate parent is33b. Retain the full grading->33b->33c identity chain.
s=s.replace("require(grading['glb_sha256']==check['immediate_source_glb_sha256'],'Actual26b immediate source mismatch')","parent=read_json(root/'captures/rightcoast_study_33b/native-check.json');require(parent['glb_sha256']==check['immediate_source_glb_sha256'] and parent['immediate_source_glb_sha256']==grading['glb_sha256'],'Actual26b to33b to33c identity mismatch')")
s=s.replace("revision=dict(revision='33c',","revision=dict(revision='33c',retained_grading_glb_sha256=grading['glb_sha256'],parent_revision_native_check_sha256=sha256(root/'captures/rightcoast_study_33b/native-check.json'),")
s=s.replace("write_json(frozen/'rightcoast-revision.json',revision)","write_json(frozen/'rightcoast-revision.json',revision);shutil.copy2(root/'captures/rightcoast_study_33b/native-check.json',frozen/'rightcoast-parent-native-check.json')")
s=s.replace('assert(revision.immediate_source_glb_sha256==grading.glb_sha256)','assert(revision.retained_grading_glb_sha256==grading.glb_sha256)\n\\tassert(revision.parent_revision_native_check_sha256==FileAccess.get_sha256(folder.path_join("rightcoast-parent-native-check.json")))\n\\tvar parent:Dictionary=JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("rightcoast-parent-native-check.json")))\n\\tassert(parent.glb_sha256==revision.immediate_source_glb_sha256 and parent.immediate_source_glb_sha256==grading.glb_sha256)')
p=R/'tools/render_rightcoast_33c.py';assert not p.exists();p.write_text(s,encoding='utf-8')
print(json.dumps(dict(changed=changed_total,working_shore=plan['working_shore']),indent=2))
