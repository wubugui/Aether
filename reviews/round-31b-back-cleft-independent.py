from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'reviews/round-30d-visible-slope-independent.py').read_text(encoding='utf-8')
src=src.replace('lantern_island_study_30d','lantern_island_study_31b').replace('round-30d-visible-slope-localization.json','round-31b-back-cleft-localization.json').replace('lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c','lantern-island-31b-20260908T195540Z-dc0f57e0a037461484c11dba7dcb8b57').replace('day-c-front.png','day-d-back.png').replace('round-30d-visible-slope-independent.json','round-31b-back-cleft-independent.json')
src=src.replace('to_bl=lambda q:np.array([q[0],-q[2],q[1]])\nto_g=lambda q:np.array([q[0],q[2],-q[1]])',"rotation_D=np.array([[math.cos(2.),0,math.sin(2.)],[0,1,0],[-math.sin(2.),0,math.cos(2.)]])\ndef to_bl(q):\n v=rotation_D.T@q;return np.array([v[0],-v[2],v[1]])\ndef to_g(q):return rotation_D@np.array([q[0],q[2],-q[1]])")
src=src.replace("cg=np.array(cam['position'])-[-3050,0,-2650]","cg=np.array(cam['position'])-[-2372,0,-1812]")
exec(compile(src,'31b_back_cleft_bounded_inverse_check','exec'))
out=R/'reviews/round-31b-back-cleft-independent.json';report=json.loads(out.read_text())
report['scope']='Four actual31b D-back cleft pixels. Independent camera inverse projection, nearest actualGLB triangle and current actual road/pad/14tree relations only; no full-support/GPU rerun.'
assert len(trees)==14
assert np.max(abs(origin-np.array([-70,65,35])))<.001
report['camera_local_blender_xyz']=origin.tolist();report['D_transform']={'position':[-2372,0,-1812],'yaw_radians':2.0}
for row in report['samples']:
 native=e['new'][row['source_name']];tri=np.array(native['vertices'])[row['source_vertex_indices']]
 row['vertices_with_protection_distances']=[{'source_vertex':i,'xyz':p.tolist(),'distance_xy_m':{n:Point(p[:2]).distance(mask) for n,mask in masks.items()}} for i,p in zip(row['source_vertex_indices'],tri)]
 row['face_y_range_m']=[float(tri[:,1].min()),float(tri[:,1].max())]
report['limits'].append('A point at y5-12 does not prove which historic cutter made the full cleft. Some sampled triangles extend beyond point positions; per-face range is recorded. New31a/b front unions do not establish rear-cleft provenance.')
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'camera':origin.tolist(),'vertices':[{'face':r['source_face'],'vertices':r['vertices_with_protection_distances'],'face_y_range_m':r['face_y_range_m']} for r in report['samples']]},indent=2))
