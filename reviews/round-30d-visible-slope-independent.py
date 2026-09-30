from pathlib import Path
exec(compile((Path(__file__).parent/'round-29a-independent-geometry.py').read_text().split('old=glb(OLD);')[0],'glb_helper','exec'))
from PIL import Image
from shapely.geometry import mapping
P=R/'captures/lantern_island_study_30d';locpath=R/'reviews/round-30d-visible-slope-localization.json';loc=json.loads(locpath.read_text());e=json.loads((P/'geometry-evidence.json').read_text());plan=json.loads((P/'proportion-plan.json').read_text());actual=glb(P/'island_c.glb');alltris=np.concatenate(list(actual.values()));keys=counter(alltris)
run=R/'captures/validation_runs/lantern-island-30d-20260908T183203Z-dfad421d9cb14734824e8942e33ac04c';png=run/'images/day-c-front.png';sidepath=Path(str(png)+'.json');side=json.loads(sidepath.read_text());cam=side['camera'];w,h=Image.open(png).size
assert sha(png)==loc['png_sha256'] and sha(sidepath)==loc['sidecar_sha256'] and sha(P/'island_c.glb')==loc['glb_sha256']
pitch,yaw,roll=cam['rotation'];assert roll==0
# Build camera world axes directly (roll zero in the actual sidecar), then
# inverse-project reported points and solve each triangle/ray linear system.
sp,cp=math.sin(pitch),math.cos(pitch);sy,cy=math.sin(yaw),math.cos(yaw)
axes=np.array([[cy,sy*sp,sy*cp],[0,cp,-sp],[-sy,cy*sp,cy*cp]])
to_bl=lambda q:np.array([q[0],-q[2],q[1]])
to_g=lambda q:np.array([q[0],q[2],-q[1]])
cg=np.array(cam['position'])-[-3050,0,-2650];origin=to_bl(cg);focal=h/2/math.tan(math.radians(cam['fov']/2))
pn=next(k for k in actual if 'footpath' in k);roadtris=actual[pn];road=unary_union([Polygon(t[:,:2]) for t in roadtris if np.cross(t[1]-t[0],t[2]-t[0])[2]>1e-9]);pads=unary_union([Polygon(s['polygon']) for s in e['sites']]);trees=[]
for p in side['placements']:
 if p.get('kind')!='existing_native_pine' or p.get('island') not in ['island_c','island_d']:continue
 base=np.array([-3050,0,-2650]) if p['island']=='island_c' else np.array(plan['d_world_position']);angle=0 if p['island']=='island_c' else plan['d_yaw'];delta=np.array(p['position'])-base;c,s=math.cos(angle),math.sin(angle);trees.append([c*delta[0]-s*delta[2],-(s*delta[0]+c*delta[2])])
masks={'actual_path':road,'expanded_pads':pads,'actual_CD_tree_axis_2m_disks':unary_union([Point(p).buffer(2) for p in trees])};protect=unary_union(list(masks.values()));a=alltris[:,0];e1=alltris[:,1]-a;e2=alltris[:,2]-a;rows=[]
for s in loc['samples']:
 p=np.array(s['hit_blender_xyz']);screen=axes.T@(to_g(p)-cg);pix=np.array([w/2+screen[0]*focal/(-screen[2])-.5,h/2-screen[1]*focal/(-screen[2])-.5]);error=float(np.linalg.norm(pix-s['pixel']));assert error<1e-6
 px,py=s['pixel'];direction=to_bl(axes@np.array([(px+.5-w/2)/focal,-(py+.5-h/2)/focal,-1.]));direction/=np.linalg.norm(direction)
 matrix=np.stack([e1,e2,np.broadcast_to(-direction,e1.shape)],axis=2);det=np.linalg.det(matrix);valid=abs(det)>1e-10;sol=np.full((len(a),3),np.nan);sol[valid]=np.linalg.solve(matrix[valid],(origin-a[valid])[...,None])[...,0];valid=valid&(sol[:,0]>=-1e-7)&(sol[:,1]>=-1e-7)&(sol[:,0]+sol[:,1]<=1+1e-7)&(sol[:,2]>0);j=int(np.where(valid,sol[:,2],np.inf).argmin());hit=origin+direction*sol[j,2];native=e['new'][s['source']['name']];f=s['source']['face'];tri=np.array(native['vertices'])[native['polygons'][f]];assert tri_key(tri)==tri_key(alltris[j]) and keys[tri_key(tri)]>0;distance=float(np.linalg.norm(hit-p));assert distance<1e-6
 poly=Polygon(tri[:,:2]);point=Point(p[:2]);relations={name:{'point_horizontal_distance_m':point.distance(mask),'face_horizontal_distance_m':poly.distance(mask),'face_projected_intersection_area_m2':poly.intersection(mask).area,'face_intersects_including_touch':poly.intersects(mask)} for name,mask in masks.items()}
 rows.append({'pixel':s['pixel'],'independent_reprojected_pixel':pix.tolist(),'pixel_error':error,'independent_nearest_actual_glb_hit':hit.tolist(),'hit_difference_m':distance,'source_name':s['source']['name'],'source_face':f,'source_vertex_indices':native['polygons'][f],'nearest_triangle_barycentric':[float(1-sol[j,0]-sol[j,1]),float(sol[j,0]),float(sol[j,1])],'face_projected_area_m2':poly.area,'protection_relations':relations,'face_free_projection_area_m2':poly.difference(protect).area,'face_free_projection':mapping(poly.difference(protect))})
report={'scope':'Six-pixel independent inverse projection plus nearest actual island-GLB ray solution and required protection proximity only. No30d full geometry/GPU rerun.','files':{str(p.relative_to(R)):sha(p) for p in [locpath,png,sidepath,P/'island_c.glb',P/'geometry-evidence.json']},'projection':'Actual sidecar zero-roll camera axes and vertical FOV; pixel centers +0.5 convention. Independently solve triangle edges/ray with 3x3 linear systems.','actual_C_D_tree_local_axes':trees,'samples':rows,'pass':True,'limits':['Distances are horizontal XY distances, not full3D clearance.','Zero intersection area can still mean boundary contact; intersects_including_touch is recorded separately.','Unprotected sample points do not authorize whole-triangle/shared-vertex changes; use the face protection intersection and cut boundary.','Nearest-hit check includes actual island GLB only; not all scene buildings/trees. Pixels were directly viewed as unobstructed grey rock.']}
(R/'reviews/round-30d-visible-slope-independent.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k in ['pixel','pixel_error','hit_difference_m','source_face','protection_relations','face_free_projection_area_m2']} for r in rows],indent=2))
