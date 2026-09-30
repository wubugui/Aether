from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'decoder','exec'))
P=R/'captures/lantern_island_study_31h';B=R/'captures/lantern_island_study_31g';e=json.loads((P/'geometry-evidence.json').read_text());base=json.loads((B/'geometry-evidence.json').read_text())['new'];assert e['old']==base and set(e['new'])==set(base) and len(base)==19
plan=json.loads((P/'reform-plan.json').read_text());rev=plan['material_revision'];tn='island_c grass and exposed rock terrain';changes=[]
for name,ob in e['new'].items():
 assert ob['vertices']==base[name]['vertices'] and ob['polygons']==base[name]['polygons']
 for i,(a,b) in enumerate(zip(base[name]['materials'],ob['materials'])):
  if a!=b:changes.append((name,i,a,b))
assert len(changes)==72 and all(a==tn and b==0 and c==2 for a,i,b,c in changes)
ob=e['new'][tn];v=np.array(ob['vertices']);faces=np.array(ob['polygons']);selected={x['polygon'] for x in rev['faces']};assert len(selected)==84 and {i for n,i,a,b in changes}<=selected
checks=[]
for fi in sorted(selected):
 t=v[faces[fi]];center=t.mean(axis=0);normal=np.cross(t[1]-t[0],t[2]-t[0]);normal/=np.linalg.norm(normal);expected=0 if center[2]>8.8 and normal[2]>.78 else 2;assert ob['materials'][fi]==expected;checks.append({'source_face':fi,'actual_material_slot':expected,'centroid_z_m':float(center[2]),'normal_z':float(normal[2])})
def exactkey(t):return tuple(sorted(tuple(map(float,p)) for p in t))
def decode_materials(path):
 data=path.read_bytes();i=12;doc=None;binary=None
 while i<len(data):
  n,k=struct.unpack_from('<II',data,i);chunk=data[i+8:i+8+n];i+=8+n
  if k==0x4e4f534a:doc=json.loads(chunk)
  elif k==0x004e4942:binary=chunk
 def acc(i):
  a=doc['accessors'][i];view=doc['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];nc={'SCALAR':1,'VEC3':3}[a['type']];stride=view.get('byteStride',np.dtype(dt).itemsize*nc)
  return np.ndarray((a['count'],nc),dtype=dt,buffer=binary,offset=view.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
 out=collections.Counter()
 for node in doc['nodes']:
  if 'mesh' not in node:continue
  assert 'matrix' not in node and node.get('translation',[0,0,0])==[0,0,0] and node.get('scale',[1,1,1])==[1,1,1] and node.get('rotation',[0,0,0,1])==[0,0,0,1]
  for prim in doc['meshes'][node['mesh']]['primitives']:
   x=acc(prim['attributes']['POSITION'])[:,[0,2,1]]*np.array([1,-1,1]);ix=acc(prim['indices']).ravel().reshape(-1,3);mat=doc['materials'][prim['material']]['name']
   for t in x[ix]:out[exactkey(t),mat]+=1
 return out
old=glb(B/'island_c.glb');new=glb(P/'island_c.glb');oc=collections.Counter(exactkey(t) for ts in old.values() for t in ts);nc=collections.Counter(exactkey(t) for ts in new.values() for t in ts);assert oc==nc
om=decode_materials(B/'island_c.glb');nm=decode_materials(P/'island_c.glb');expected=om.copy();grass=rev['slots'][0];rock=rev['slots'][2]
for name,fi,a,b in changes:
 key=exactkey(v[faces[fi]]);assert expected[key,grass]>0;expected[key,grass]-=1;expected[key,rock]+=1
assert +expected==nm
report={'round':'31h','scope':'Independent19native geometry exact equality plus actualGLB exact-float triangle/material counters; no repeated support or intersection scan.','files':{str(p.relative_to(R)):sha(p) for p in [B/'island_c.glb',P/'island_c.glb',P/'geometry-evidence.json',P/'reform-plan.json']},'native_objects':19,'all_native_vertices_and_polygons_exact31g':True,'all_nonterrain_materials_unchanged':True,'actual_all_GLB_triangle_counter_exact_no_rounding':True,'actual_total_triangles':sum(nc.values()),'actual_GLB_material_triangle_counter_matches_only72_expected_changes':True,'selected_replacement_faces':84,'material_changes':72,'stone_faces':sum(a['actual_material_slot']==2 for a in checks),'retained_upper_grass_faces':sum(a['actual_material_slot']==0 for a in checks),'material_slots':{'0':grass,'2':rock},'actual_source_rule_checks':checks,'support_and_intersection_evidence_reused_from31g':['reviews/round-31g-independent-geometry.json','reviews/round-31g-actual-tree-support.json','reviews/round-31g-local-intersections.json'],'geometry_and_material_identity_pass':True,'pass':True,'visual_complete':False,'full_reference_accepted':False,'limits':['31g geometric support/intersection evidence transfers because all actual triangle coordinates exactly match; runtime31h binding and placements still checked by root.','Material correction does not prove shoulder shape or reference match.','No Blender/GPU/support/intersection rerun.']}
(R/'reviews/round-31h-independent-material-geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(R/'reviews/round-31h-independent-material-geometry.md').write_text('# 31h 材质与几何同一性独立核验\n\n通过。19个原生对象的顶点、面及面顺序与31g逐项完全相同；全部实际GLB三角按原始浮点坐标计数集完全相同，未用四舍五入容差掩盖位置变化。\n\n84个重接面中72面由草slot0改为石slot2，12个满足质心z>8.8m且法线z>0.78的上坡面保留草。以实际三角重算法线和质心逐面核对，并独立解码实际GLB的材质对应，确认只有这72项变化；其他材质保持。原生名称：slot0='+grass+'，slot2='+rock+'。\n\n因此复用31g道路/pad/真实树干支承及局部离散自交证据，没有重新扫描。31h运行绑定与落点由root另核验；材质修正不等于岩肩造型完成，仍待五原图。`full_reference_accepted=false`。\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['files','actual_source_rule_checks']},indent=2))
