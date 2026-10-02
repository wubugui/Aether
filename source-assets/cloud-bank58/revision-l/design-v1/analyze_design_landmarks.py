"""Offline projection + NEW design landmark rays; not a model builder or renderer.
Uses the archived grids; does NOT run or rewrite the old footprint survey.
"""
from pathlib import Path
import json,os,sys,struct,importlib.util,hashlib
P=Path(__file__).resolve().parent
R=Path(os.environ.get('AETHER_ROOT',str(P.parent/'Aether'))).resolve()
os.environ['MPLCONFIGDIR']=str(P/'mpl-cache');os.environ['XDG_CACHE_HOME']=str(P/'diagram-cache')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
D=json.loads((P/'design_plan.json').read_text());G=np.load(P/'survey-grids.npz');xs,zs=G['xs'],G['zs'];M=np.isfinite(G['CloudSea_1_1_top'])
S=R/'source-assets/cloud-bank58/revision-k/world-trial-v1/provenance58k.py'
spec=importlib.util.spec_from_file_location('new_landmark_ray_only',S);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.NEIGHBORS=['CloudSea_0_0','CloudSea_0_1','CloudSea_0_2','CloudSea_1_0','CloudSea_1_2','CloudSea_2_0','CloudSea_2_1','CloudSea_2_2'];clouds=m.decode_clouds()
E=json.loads((P/'evidence-bindings.json').read_text());front=E['fixed_actual_camera_records'][1]
v=np.array(struct.unpack('<12f',bytes.fromhex(front['camera_transform'])[4:]));B=v[:9].reshape(3,3);O=v[9:];pr=np.array(struct.unpack('<16f',bytes.fromhex(front['camera_projection'])[4:]));out=[]
fig,ax=plt.subplots(figsize=(12,7.2),layout='constrained');colors=['#bc8332','#be6955','#298b88','#577dae']
for k,c in enumerate(D['controls'][:4]):
 cx,cz=c['world_center_xz_m'];sx,sz=c['plan_span_xz_m'];points=[('crest',[cx,c['default_crest_y_m'],cz],'new crest assumption')]
 for j,a in enumerate(np.linspace(0,2*np.pi,12,endpoint=False)):
  x=cx+.45*sx*np.cos(a);z=cz+.45*sz*np.sin(a);ix=np.argmin(abs(xs-x));iz=np.argmin(abs(zs-z))
  if not M[iz,ix]:continue
  y=c['default_crest_y_m']-(95+25*np.cos(a+0.6*k));status='new upper/lower shoulder assumption'
  if any(np.isfinite(G[n+'_top'][iz,ix]) for n in m.NEIGHBORS):y=float(G['CloudSea_1_1_top'][iz,ix]);status='proposed collar follows old grid top; actual collar remains to be conformed'
  points.append((f'shoulder{j:02}',[float(x),float(y),float(z)],status))
 rows=[]
 for label,pos,status in points:
  point=np.array(pos);q=np.linalg.solve(B,point-O);ndc=q[:2]/(-q[2])*[pr[0],pr[5]]
  hits={name:float(hit) for name,row in clouds.items() if (hit:=m.ray_hits(O,point,row['triangles'])) is not None}
  rows.append({'label':label,'world_xyz_m':pos,'status':status,'ndc_xy':ndc.tolist(),'depth_m':float(-q[2]),'in_frame_as_point':bool(q[2]<0 and np.all(abs(ndc)<=1)),'earlier_actual_neighbor_triangle_hits_m':hits,'clear_in_this_bounded_neighbor_test':not bool(hits),'actual_new_surface_or_pixel_visibility_proven':False})
 ndc=np.array([r['ndc_xy'] for r in rows]);frame=(ndc+1)/2;frame[:,1]=1-frame[:,1]
 inside=[r for r in rows if r['in_frame_as_point']]
 result={'id':c['id'],'landmark_count':len(rows),'screen_domain_method':'Bounding rectangle of proposed sparse crest/shoulder landmarks in original front projection; not a silhouette, occupied area, native pixels, or visible area','unclipped_frame_fraction_bounds_xy':[frame.min(0).tolist(),frame.max(0).tolist()],'in_frame_landmarks':len(inside),'in_frame_and_clear_of_tested_neighbors':sum(r['clear_in_this_bounded_neighbor_test'] for r in inside),'all_clear_of_tested_neighbors':sum(r['clear_in_this_bounded_neighbor_test'] for r in rows),'rows':rows};out.append(result)
 hull=ConvexHull(frame).vertices;ax.fill(frame[hull,0],frame[hull,1],alpha=.10,color=colors[k]);ax.plot(np.r_[frame[hull,0],frame[hull[0],0]],np.r_[frame[hull,1],frame[hull[0],1]],color=colors[k],ls='--',lw=1.3)
 for r,xy in zip(rows,frame):ax.scatter(xy[0],xy[1],marker='o' if r['clear_in_this_bounded_neighbor_test'] else 'x',color=colors[k],s=40)
 center=frame[0];ax.annotate('ABCD'[k]+' crest',xy=center,xytext=(center[0]-.03,center[1]-.045-0.04*(k%2)),fontsize=12,color=colors[k],weight='bold',arrowprops=dict(arrowstyle='->',color=colors[k]))
ax.add_patch(plt.Rectangle((0,0),1,1,fill=False,lw=2,color='#273448'));ax.axvspan(1,1.25,color='#eeeeee',zorder=-2);ax.set(xlim=(.30,1.30),ylim=(.76,.28),xlabel='Fraction of original front frame width (1.0 = right edge)',ylabel='Fraction of frame height (0 = top)',title='PROPOSED landmarks: right-half detail of the exact original front projection\nDots: clear of 8 tested old clouds; crosses: actual old-cloud triangle hit')
ax.grid(alpha=.2);fig.suptitle('Offline design-point diagram, NOT a new surface or actual visible-pixel result',fontsize=15,weight='bold');fig.savefig(P/'05-original-front-landmark-domains.png',dpi=160);plt.close(fig)
data={'version':'new-design-landmark-rays-v1','status':'New assumed landmarks only. Existing saved indexed neighbor triangles, no new mesh/native rendering.','source_scene':str(m.SCENE.relative_to(R)),'source_scene_sha256':hashlib.sha256(m.SCENE.read_bytes()).hexdigest(),'decoder_sha256':hashlib.sha256(S.read_bytes()).hexdigest(),'scope':m.NEIGHBORS,'not_recomputed':'Archived footprint survey and its four files were not rerun or changed. This is a distinct bounded query from the old front camera to new proposed landmark positions.','limitations':['No candidate surface exists, so no self-occlusion test','Ship and other noncloud geometry not tested','Sparse control/shoulder landmarks are not a silhouette or pixel-coverage mask','A frustum-excluded center does not prove the entire cloud crown is outside the frame','Saved-cloud ray queries are offline float64 diagnostics, not native measurements'],'groups':out}
(P/'design-landmarks.json').write_text(json.dumps(data,indent=2)+'\n')
for r in out:print(r['id'],np.array(r['unclipped_frame_fraction_bounds_xy']).round(4).tolist(),r['in_frame_landmarks'],r['in_frame_and_clear_of_tested_neighbors'],'/',r['landmark_count'])
