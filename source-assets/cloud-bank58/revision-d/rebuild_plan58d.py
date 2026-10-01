"""D design reconstructed from this task's surviving context after workspace reset.

The earlier325vertex/646triangle draft was generated, never validated. This is
new local material, not a recovered old verification or visual acceptance.
"""
import json,math,hashlib,os
from pathlib import Path
import numpy as np
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
right=np.array([.685364723205566,0,.72819995880127]);forward=np.array([.72819995880127,0,-.685364723205566]);anchor=np.array([3958.,0.,3667.])
def world(q):u,v,y=q;return (anchor+right*u+forward*v+[0,y,0]).tolist()
curves=[]
def add(name,role,points,widths):curves.append(dict(id=name,role=role,knots_local_uv_and_worldY_m=points,knots_godot_world_xyz_m=[world(q) for q in points],left_right_halfwidth_m=widths,native_type='Editable POLY curve; no bevel geometry or separate cap'))
add('R1','primary',[[-230,35,720],[-120,100,885],[-25,65,910],[100,120,820],[190,160,735]],[[70,95],[60,80],[80,60],[65,85],[50,65]])
add('R2','primary',[[-25,65,910],[20,-45,810],[-25,-155,735],[70,-240,640]],[[65,75],[55,80],[55,70],[40,45]])
add('R3','primary',[[100,120,820],[130,15,815],[250,-10,690]],[[55,65],[60,75],[45,55]])
medium=[
 ('F1',[[-200,65,780],[-220,-20,760],[-160,-95,650]],[[40,55],[45,55],[35,40]]),
 ('F2',[[-110,94,876],[-165,150,800],[-195,245,660]],[[35,50],[45,55],[30,45]]),
 ('F3',[[-35,70,890],[-60,165,795],[5,220,675]],[[35,50],[40,55],[35,40]]),
 ('F4',[[85,105,822],[110,190,755],[175,225,680]],[[30,45],[40,45],[30,40]]),
 ('F5',[[20,-35,805],[90,-110,725],[140,-185,625]],[[35,45],[45,55],[30,45]]),
 ('F6',[[-20,-125,750],[-120,-150,675],[-145,-250,575]],[[35,45],[40,55],[30,40]]),
 ('F7',[[170,10,775],[210,-60,680],[275,-95,570]],[[30,50],[35,45],[25,35]]),
 ('F8',[[-195,-60,720],[-265,-110,660],[-235,-200,565]],[[30,40],[40,45],[25,35]])]
for n,q,w in medium:add(n,'medium',q,w)
small=[
 ('E1',[[-240,15,730],[-265,-10,700],[-250,-50,640]]),('E2',[[-150,85,865],[-165,45,810],[-135,5,730]]),
 ('E3',[[-80,70,885],[-65,30,840],[-85,-5,780]]),('E4',[[35,90,855],[70,65,825],[80,35,750]]),
 ('E5',[[135,125,795],[165,90,750],[195,70,700]]),('E6',[[-170,170,780],[-210,175,725],[-225,205,650]]),
 ('E7',[[-45,170,785],[-10,160,735],[15,185,675]]),('E8',[[100,180,765],[140,175,720],[155,205,660]]),
 ('E9',[[45,-70,780],[15,-100,750],[40,-130,685]]),('E10',[[-95,-165,670],[-80,-205,630],[-110,-235,570]]),
 ('E11',[[100,-115,720],[130,-140,680],[115,-170,610]]),('E12',[[210,-55,680],[235,-25,625],[260,-55,570]])]
for n,q in small:add(n,'small',q,[[15,25],[20,30],[15,20]])
returns=[
 ('U1',[[-235,-200,565],[-270,-220,465],[-235,-190,315],[-120,-160,270]]),
 ('U2',[[70,-240,640],[110,-290,530],[60,-265,360],[-20,-145,310]]),
 ('U3',[[275,-95,570],[305,-80,470],[260,-50,280],[130,-5,250]]),
 ('U4',[[175,225,680],[205,260,565],[170,210,360],[55,125,330]]),
 ('U5',[[-195,245,660],[-235,245,535],[-195,190,355],[-85,75,300]]),
 ('U6',[[-265,-110,660],[-305,-85,500],[-270,-45,340],[-120,5,245]])]
for n,q in returns:add(n,'side_under_return',q,[[40,55],[35,55],[30,50],[40,60]])
for n,q in [('B1',[[-160,-120,260],[-70,-70,180],[45,-20,240],[140,80,300]]),('B2',[[130,-5,250],[80,-100,170],[-20,-145,310]]),('B3',[[-85,75,300],[-35,150,210],[55,125,330]])]:add(n,'under_fold',q,[[40,55]]*len(q))
for r in curves:
 factor=.8 if r['id'] in('F2','F3','F4') else .7 if r['id'] in('E6','E7','E8') else 1
 r['left_right_halfwidth_m']=[[a*factor,b*factor] for a,b in r['left_right_halfwidth_m']]
parents={'F1':'R1','F2':'R1','F3':'R1','F4':'R1','F5':'R2','F6':'R2','F7':'R3','F8':'F1','E1':'F1','E2':'R1','E3':'R1','E4':'R1','E5':'R3','E6':'F2','E7':'F3','E8':'F4','E9':'R2','E10':'F6','E11':'F5','E12':'F7'}
lookup={r['id']:r for r in curves}
for child,parent in parents.items():
 r=lookup[child];q=np.array(r['knots_local_uv_and_worldY_m'][0],float);pp=np.array(lookup[parent]['knots_local_uv_and_worldY_m'],float);best=None
 for i,(a,b) in enumerate(zip(pp,pp[1:])):
  delta=b[:2]-a[:2];t=float(np.clip((q[:2]-a[:2])@delta/(delta@delta),0,1));point=a+(b-a)*t;distance=float(np.linalg.norm(q[:2]-point[:2]))
  if best is None or distance<best[0]:best=(distance,i,t,point)
 distance,i,t,point=best;r['initial_start_before_junction']=q.tolist();r['knots_local_uv_and_worldY_m'][0]=point.tolist();r['knots_godot_world_xyz_m'][0]=world(point);r['shared_parent_junction']=dict(parent_curve=parent,parent_segment=i,parameter=t,local_uv_worldY=point.tolist())
valleys=[]
for n,q,band in [('Vd',[[-200,-230,515],[-155,-145,550],[-110,-75,590],[-75,-10,630]],[480,680]),('Vback',[[-135,250,560],[-110,185,600],[-95,140,630]],[500,700])]:
 valleys.append(dict(id=n,knots_local_uv_and_worldY_m=q,knots_godot_world_xyz_m=[world(x) for x in q],half_width_m=20,first_surface_worldY_band_m=band,first_solid_interval_minimum_m=160,station_spacing_m=25))
outline=[[-300,-100],[-230,-290],[-75,-315],[70,-235],[200,-265],[310,-105],[265,40],[300,150],[125,290],[-10,230],[-130,310],[-265,175],[-230,35],[-330,-10]]
source=ROOT/'cloud-evidence/cloudsea52h-d-ab-front-20261001T102736Z-svczz9fo/images/report.json';camera=json.loads(source.read_text())['captures'][0];B=np.array(camera['camera_transform'][:9]).reshape(3,3).T;O=np.array(camera['camera_transform'][9:]);inv=np.linalg.inv(B);projection=np.array(camera['camera_projection_columns']).T
projected=[]
for r in curves:
 cc=(np.array(r['knots_godot_world_xyz_m'])-O)@inv.T;clip=np.c_[cc,np.ones(len(cc))]@projection.T;ndc=clip[:,:3]/clip[:,3:];pixels=np.c_[(ndc[:,0]+1)*836,(1-ndc[:,1])*470.5];projected.append(dict(id=r['id'],role=r['role'],knot_reference_pixels=pixels.tolist(),depth_range_m=[float((-cc[:,2]).min()),float((-cc[:,2]).max())],not_actual_surface_visibility=True))
plan=dict(status='Context-reconstructed D design; no old validation claimed',reconstructed_after_workspace_reset=True,baseline_commit='4bff917',reference='ref/1216.png',anchor_godot_world_xyz=anchor.tolist(),local_u_world=right.tolist(),local_v_world=forward.tolist(),horizontal_local_extent_m=[640,625],outline_local_uv=outline,curves=curves,valley_controls=valleys,camera={k:camera[k] for k in ['camera_transform','camera_projection_columns','camera_fov','camera_near','camera_far']},camera_source=str(source.relative_to(ROOT)),camera_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),projected_curves=projected,scope='One640x625m fold junction. Do not expand to4roots or world before actual small-source images. First cage has3main/8medium,6side and3belly curves;12small curves are guidance only.',method='Single closed native crease cage with shared ridge/valley cells, folded3D sides and an unequal-depth underside. No voxel union, separate hats, smooth primitive or flat bottom cap.',geometry_passed=False,visual_acceptance=False,blender_started=False)
(P/'control-plan58d.json').write_text(json.dumps(plan,indent=2)+'\n');print('Reconstructed',len(curves),'curves and',len(parents),'shared junctions')
