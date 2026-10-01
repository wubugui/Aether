"""C source PLAN only: reference hierarchy,57 control specifications and diagram.

No Blender, mesh construction, renderer, world load, source mutation or geometry
validation. Polygon extents in the diagram are schematic control guides only.
"""
import json,math,os
from pathlib import Path
P=Path(__file__).resolve().parent;A=P.parent;ROOT=A.parents[1]
os.environ.setdefault('MPLCONFIGDIR','/tmp/feiting58c-matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/feiting58c-cache')
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

intake=json.loads((A/'native-intake58.json').read_text())
roots=[r for r in intake['roots'] if r['selected']]
camera=[3000,1150,4300];right=[.6853647232,.7281999588];forward=[.7281999588,-.6853647232]
controls=[]
def add(name,role,center,size,yaw,meaning,parent=None):
    x,y,z=center;dx=x-camera[0];dz=z-camera[2]
    row=dict(id=name,role=role,center_godot_world_xyz_m=center,design_extent_xyz_m=size,yaw_degrees=yaw,
             authoring_description=meaning,parent_form=parent,camera_relative_right_m=dx*right[0]+dz*right[1],
             camera_horizontal_depth_m=dx*forward[0]+dz*forward[1],
             actual_mesh_built=False,coverage_or_connection_verified=False)
    controls.append(row);return row

lower=[
 ('L01',[2950,515,3760],[650,510,730],-22,'Unequal west underside; connectsL02/L05, no perimeter rail'),
 ('L02',[3220,450,4220],[730,570,700],18,'Deep near-left belly; separate lowest point, not a common bottom'),
 ('L03',[3750,505,4180],[820,540,710],-10,'Broad near-center density underV1, independently folded underside'),
 ('L04',[4340,475,4080],[750,610,760],31,'Near-right deep body, oblique shoulder towardL06'),
 ('L05',[3590,505,3540],[880,500,870],9,'Central solid junction beneath intersecting valley corridors'),
 ('L06',[4250,485,3480],[890,530,810],-17,'Broad middle-right volume; no hollow ring connection'),
 ('L07',[3260,520,2980],[840,510,670],22,'Unequal far-left support; staggered againstL08'),
 ('L08',[3930,485,2870],[910,510,750],6,'Broad far-center support underV2; thick physical body'),
 ('L09',[4590,500,2820],[830,530,870],-23,'Far-right support with outward taper; not a rectangular trim')]
for n,c,s,y,m in lower:add(n,'lower_density',c,s,y,m)
primary=[
 ('P01',[3060,790,3800],[490,310,470],-21,'Near-left compact shoulder; broad uneven crown, not a cone'),
 ('P02',[3720,835,4110],[590,370,520],19,'Largest near crown; one offset angular lip is allowed'),
 ('P03',[4270,805,4280],[520,350,460],-34,'Near-right interrupted short ridge; different axis fromP02'),
 ('P04',[3540,800,3200],[470,280,390],37,'Middle-left short ridge separated by a real supported valley'),
 ('P05',[4180,820,3430],[440,310,370],-13,'Middle-right compact fork, secondary toP02'),
 ('P06',[4570,780,2700],[350,240,310],21,'Smaller local far-edge crest, not the full horizon cloud layer')]
for n,c,s,y,m in primary:add(n,'primary_crown',c,s,y,m)
lookup={r['id']:r for r in controls}
medium=[
 ('P01',[-140,-30,-220],[230,180,250],-10,'rear folded shoulder'),('P01',[180,-70,120],[270,150,190],30,'short side-return'),('P01',[-190,-100,170],[240,160,210],-35,'falling front fold'),
 ('P02',[-240,-55,80],[300,200,250],-25,'wide crown-side saddle'),('P02',[170,-20,-210],[260,180,240],5,'uneven high back shoulder'),('P02',[220,-110,200],[290,170,230],25,'low split front fold'),('P02',[-120,-120,-220],[230,160,280],10,'valley-facing broad ledge'),
 ('P03',[230,-65,-80],[280,160,230],-15,'short outer broken shoulder'),('P03',[-180,-35,-190],[230,200,260],25,'offset high inner shoulder'),('P03',[60,-115,220],[280,170,220],-35,'downward front lobe'),
 ('P04',[-160,-30,-150],[200,150,220],25,'middle back fold'),('P04',[190,-80,90],[240,160,200],-20,'middle oblique saddle'),('P04',[-100,-90,180],[200,130,220],40,'middle front short lip'),
 ('P05',[160,-50,-150],[210,170,180],-25,'middle-right back fold'),('P05',[-150,-90,120],[220,140,180],10,'inner low shoulder'),('P05',[120,-110,140],[190,130,200],35,'outer short return'),
 ('P06',[-140,-20,-80],[180,140,150],-15,'local far smaller fold'),('P06',[150,-60,100],[160,130,190],25,'local far edge break')]
for i,(parent,offset,size,yaw,meaning) in enumerate(medium,1):
    c=[x+y for x,y in zip(lookup[parent]['center_godot_world_xyz_m'],offset)]
    row=add(f'M{i:02}','medium_fold',c,size,yaw,meaning,parent);lookup[row['id']]=row
small=[
 ('M01',[-50,95,-45],[90,80,75],-12),('M02',[85,60,55],[100,65,80],35),('M03',[-85,65,50],[75,85,95],10),
 ('M04',[-90,90,45],[120,85,100],-25),('M04',[50,115,-35],[85,95,80],30),('M05',[80,70,-65],[110,90,80],15),
 ('M06',[95,65,40],[105,80,90],-30),('M06',[-65,80,-45],[80,70,95],20),('M07',[-60,65,85],[90,65,85],35),
 ('M08',[90,70,-35],[100,80,75],-15),('M09',[-70,90,-65],[90,85,95],20),('M09',[60,70,65],[80,70,95],-20),
 ('M10',[70,65,55],[105,75,80],30),('M11',[-45,65,-50],[75,60,70],-5),('M12',[65,70,35],[80,65,75],-25),
 ('M13',[-55,55,65],[65,70,75],20),('M14',[55,70,-45],[75,70,60],-15),('M15',[-60,55,35],[80,55,70],25),
 ('M16',[50,55,60],[65,60,75],-30),('M17',[-50,65,-35],[60,55,65],15),('M18',[45,55,50],[60,55,70],-20),
 ('M18',[-35,60,-40],[55,50,60],30),('P02',[65,160,-35],[85,110,75],-15),('P04',[-45,135,20],[70,80,65],25)]
for i,(parent,offset,size,yaw) in enumerate(small,1):
    c=[x+y for x,y in zip(lookup[parent]['center_godot_world_xyz_m'],offset)]
    add(f'S{i:02}','small_edge_fold',c,size,yaw,'Rare angular lip' if i in (23,24) else 'Localized edge change tied to its parent shoulder; not uniform scatter',parent)

valleys=[
 dict(id='V1',name='Broken diagonal flight-side valley',xz=[[3290,4060],[3400,3820],[3810,3700],[3990,3430],[4460,3150]],half_width_m=60,
      support_controls=['L02','L03','L05','L06','L09'],intended_floor_y_range_m=[460,790]),
 dict(id='V2',name='Short transverse middle fold',xz=[[3360,3370],[3490,3540],[3740,3510],[3950,3200],[4220,3140]],half_width_m=50,
      support_controls=['L05','L07','L08','L06'],intended_floor_y_range_m=[460,780])]
sections=[dict(id='SCT1',plane='world_z',value_m=3800,range_x_m=[2750,4770]),
          dict(id='SCT2',plane='world_x',value_m=3800,range_z_m=[2580,4480]),
          dict(id='SCT3',plane='world_z',value_m=3100,range_x_m=[2850,4970])]
reference=[
 dict(layer='near',approximate_pixel_region_xy=[0,490,1672,941],large_width_px=[150,400],medium_width_px=[45,140],small_width_px=[10,45],
      observed='Several partially cropped, irregular thick masses; nested shoulders and short folds; downward bodies are distinct; no enclosing oval rim'),
 dict(layer='middle',approximate_pixel_region_xy=[50,425,1660,640],large_width_px=[45,140],medium_width_px=[15,55],small_width_px=[4,20],
      observed='Short overlapping crowns, staggered relief and branching bright ridges; dark valleys retain modeled-looking cloud structure, not flat empty water'),
 dict(layer='far_horizon',approximate_pixel_region_xy=[400,365,1672,465],large_width_px=[8,35],medium_width_px=[3,12],small_width_px=[1,5],
      observed='Dense small relief merges into bright nearly horizontal bands; individual repeated large spheres are absent'),
 dict(layer='upper_layers',approximate_pixel_region_xy=[0,35,1672,410],long_width_px=[180,700],typical_band_thickness_px=[10,55],occasional_peak_height_px=[35,110],
      observed='Wide thin horizontal bodies and sparse angular rising peaks; cloud layers recede in height and overlap')]
plan=dict(status='PLAN ONLY. NoC mesh, Blender process, render or world.',reference_path='ref/1216.png',reference_size_px=[1672,941],
          reference_interpretation='Manual approximate pixel intervals after actually viewing the original; overlapping depth bands, not segmented masks. Pixel size is not a recovered physical dimension.',
          reference_layers=reference,selected_saved52f_roots=roots,research_scene_sha256=intake['source_scene_sha256'],camera_godot_world=camera,
          local_patch_not_full_horizon=True,unmodified_external_roots=21,controls=controls,control_counts={role:sum(r['role']==role for r in controls) for role in sorted(set(r['role'] for r in controls))},
          shape_rules=['No rectangular clipping/domain shell or common underside cap','No perimeter loop made from long constant-radius lofts','Lower supports are nine independently shaped compact unequal3D bodies, not repeated meshes','Primary crowns short and unequal; shoulders carry substantial visible mass','Small folds localized to edges, with only two rare high lips','Native geometry must retain hard low-poly faces; smoothing and triangle count are not quality targets'],
          valley_corridors=valleys,section_planes=sections,
          required_native_checks=dict(vertical_rays='After actual mesh construction, cast fromworldY1500 downward through every25m valley path station and transverse offsets−half_width,0,+half_width. Use real triangles and report all entry/exit intervals.',
                                      required_cloud_support='Every intended valley ray must intersect a real closed cloud interval at least160m thick; its first cloud surface should be within the declared floor band. Missing rays fail. Do not fillAABB or add a plane.',
                                      cross_sections='Intersect actual final triangles withSCT1/SCT2/SCT3; retain top/bottom contours and real solid intervals. No inferred filled height map.',
                                      topology='One orientable closed lower shell, zero boundary/nonmanifold/self-intersections and genus0 for this dense local proposal; no unplanned through-slot. Do not weaken gates for modeling artifacts.',
                                      view_and_context='Five full source faces first, then actual21-root contact/inside/outside source context if authorized. Four roots do not establish the full bright horizon.',
                                      flight='Check original camera point against actual closed triangles; sampled center clearance is not full ship or swept-route clearance'),
          every_geometry_and_visual_gate_pending=True,world_changed=False,visual_acceptance=False)
(P/'control-plan58c.json').write_text(json.dumps(plan,indent=2)+'\n')

colors={'lower_density':'#5c88a3','primary_crown':'#bf7839','medium_fold':'#d59b4b','small_edge_fold':'#e0bc65'}
polyprofile=[[-.48,-.34],[-.12,-.52],[.35,-.42],[.52,-.08],[.35,.38],[-.03,.5],[-.45,.28]]
def extent(row):
    x,y,z=row['center_godot_world_xyz_m'];w,h,d=row['design_extent_xyz_m'];t=math.radians(row['yaw_degrees']);co,si=math.cos(t),math.sin(t)
    return [(x+co*px*w-si*pz*d,z+si*px*w+co*pz*d) for px,pz in polyprofile]
fig,axes=plt.subplots(1,2,figsize=(17,9),gridspec_kw={'width_ratios':[1.4,1]})
ax=axes[0];ax.set_facecolor('#f4f3ee')
for root in roots:
    x,y,z=root['position'];ax.add_patch(Polygon([(x-575,z-575),(x+575,z-575),(x+575,z+575),(x-575,z+575)],closed=True,fill=False,edgecolor='#81888b',linestyle='--',linewidth=1))
    ax.plot(x,z,'+',color='#4f5458',markersize=8);ax.text(x-535,z+500,root['name'],fontsize=8,color='#4f5458')
for row in controls:
    role=row['role'];alpha={'lower_density':.17,'primary_crown':.40,'medium_fold':.38,'small_edge_fold':.70}[role]
    ax.add_patch(Polygon(extent(row),closed=True,facecolor=colors[role],edgecolor=colors[role],alpha=alpha,linewidth=.8))
    if role in ('lower_density','primary_crown'):
        x,y,z=row['center_godot_world_xyz_m'];ax.text(x,z,row['id'],fontsize=8,ha='center',va='center',weight='bold',color='#24333e')
for valley in valleys:
    xx,zz=zip(*valley['xz']);ax.plot(xx,zz,color='#95244e',lw=2,marker='o',ms=3);ax.text(xx[-1]+35,zz[-1],valley['id'],color='#95244e',weight='bold')
for s in sections:
    if s['plane']=='world_z':ax.plot(s['range_x_m'],[s['value_m']]*2,color='#66856b',lw=1,ls=':');ax.text(s['range_x_m'][0],s['value_m']+25,s['id'],fontsize=8,color='#406347')
    else:ax.plot([s['value_m']]*2,s['range_z_m'],color='#66856b',lw=1,ls=':');ax.text(s['value_m']+25,s['range_z_m'][0],s['id'],fontsize=8,color='#406347')
ax.plot(camera[0],camera[2],'o',color='#172c44',ms=7);ax.annotate('1216 camera\nY=1150m',xy=(camera[0],camera[2]),xytext=(2560,4570),arrowprops=dict(arrowstyle='->',color='#172c44'),fontsize=9)
ax.arrow(camera[0],camera[2],forward[0]*420,forward[1]*420,width=9,head_width=65,color='#172c44',length_includes_head=True)
ax.set_xlim(2450,5200);ax.set_ylim(2320,4730);ax.set_aspect('equal');ax.set_xlabel('Godot world X (m)');ax.set_ylabel('Godot world Z (m)')
ax.set_title('C: four-root arrangement and supported-valley test routes\nSchematic control extents only; not a cloud mesh or coverage result',fontsize=12)
ax.grid(alpha=.15)
bx=axes[1];bx.set_facecolor('#f4f3ee')
for row in controls:
    if row['role']=='lower_density':continue
    role=row['role'];size={'primary_crown':180,'medium_fold':75,'small_edge_fold':28}[role]
    bx.scatter(row['camera_relative_right_m'],row['camera_horizontal_depth_m'],s=size,c=colors[role],alpha=.8,edgecolors='#584a3c',linewidths=.3)
    if role=='primary_crown':bx.text(row['camera_relative_right_m']+25,row['camera_horizontal_depth_m'],row['id'],fontsize=8)
bx.axhline(1050,color='#7f8586',lw=1,ls='--');bx.axhline(1900,color='#7f8586',lw=1,ls='--')
bx.text(-1200,450,'NEAR: largest compact crowns\nshoulders are a major visible layer',fontsize=9)
bx.text(-1200,1400,'MIDDLE: shorter / smaller / staggered',fontsize=9)
bx.text(-1200,2300,'LOCAL FAR EDGE only\nFull horizon remains outside this four-root task',fontsize=9)
bx.set_xlim(-1300,1450);bx.set_ylim(0,2850);bx.set_xlabel('Camera-right horizontal offset (m)');bx.set_ylabel('Horizontal depth from original1216 camera (m)')
bx.set_title('Planned hierarchy:6 primary +18 medium +24 small\n9 lower density bodies sit beneath these forms',fontsize=12);bx.grid(alpha=.15)
fig.suptitle('C PLAN ONLY — no model built; every ray/section/visual gate remains pending',fontsize=14,weight='bold')
fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(P/'world-plan58c.svg');fig.savefig(P/'world-plan58c.png',dpi=120);plt.close(fig)
print(json.dumps({'controls':len(controls),'counts':plan['control_counts'],'files':['control-plan58c.json','world-plan58c.svg','world-plan58c.png'],'mesh_built':False},indent=2))
