"""Sculpt saved terrain tiles using authored ridges and a connected tidal estuary."""
from pathlib import Path
import bpy,numpy as np,json,hashlib,shutil,math
R=Path(__file__).resolve().parents[1];OUT=R/'captures/highcoast_study_36a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
intake=json.loads((R/'reviews/36-terrain-savedmesh-intake.json').read_text())
# Explicit sculpting controls in world X,Z, height above existing shore, width.
# Different spine heights and branches make connected masses, not isolated cones.
RIDGES=[
    [[-2450,-2420,75,190],[-2360,-2620,135,260],[-2200,-2790,230,330],[-1960,-2900,300,370],[-1740,-2840,220,300]],
    [[-3040,-3550,105,240],[-2840,-3630,235,320],[-2530,-3710,415,400],[-2280,-3880,345,350],[-2030,-4130,210,270]],
    [[-2800,-3970,180,260],[-2510,-3710,405,320],[-2200,-3560,290,330],[-1910,-3510,195,280]],
    [[-1800,-3050,180,250],[-1560,-3260,295,320],[-1340,-3480,250,290],[-1160,-3750,130,220]],
    [[-2710,-2750,55,120],[-2480,-2810,125,180],[-2200,-2790,215,190]],
    [[-3300,-3840,90,160],[-3080,-3750,140,240],[-2840,-3630,225,250]],
]
RIVER=[[-3090,-3190,96],[-2840,-3200,80],[-2640,-3130,63],[-2450,-3220,57],[-2240,-3310,52],[-2030,-3240,48],[-1840,-3370,42],[-1610,-3300,10]]
def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def nearest_line(points,x,z):
    best=np.full(x.shape,np.inf);values=[np.zeros_like(x) for _ in range(len(points[0])-2)];fractions=np.zeros_like(x)
    for i,(a,b) in enumerate(zip(points[:-1],points[1:])):
        dx=b[0]-a[0];dz=b[1]-a[1]
        t=np.clip(((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz),0,1)
        distance=np.hypot(x-(a[0]+t*dx),z-(a[1]+t*dz));take=distance<best
        best=np.where(take,distance,best)
        for k in range(len(values)):values[k]=np.where(take,a[k+2]+t*(b[k+2]-a[k+2]),values[k])
        fractions=np.where(take,(i+t)/(len(points)-1),fractions)
    return best,values,fractions
def sculpt_height(x,z,old):
    coast=-1900.+(z+1500.)*(2300./3500.)
    inland=x-coast
    edge=smooth(-3750,-3540,x)*(1-smooth(-1120,-900,x))*smooth(-4400,-4210,z)*(1-smooth(-2360,-2150,z))
    # Broken coastal shoulders descend to a real low shore at the original sea.
    rim=38.+48.*(.5+.5*np.sin((z+2700.)*.007))
    shore=6.+rim*smooth(30,105,inland)
    shore*=1-smooth(190,500,inland)
    target=np.maximum(15.,shore)
    for ridge in RIDGES:
        distance,(height,width),t=nearest_line(ridge,x,z)
        profile=np.maximum(0.,1.-distance/width)**1.15
        target=np.maximum(target,15.+height*profile)
    # A low, connected tidal channel (sea-level water), not a fake painted river.
    distance,(halfwidth,),t=nearest_line(RIVER,x,z)
    end_fade=1-smooth(.91,1.,t)
    channel=np.maximum(halfwidth,8.)
    bed=-5.+3.*t
    bank=bed+(7.-bed)*smooth(channel*.68,channel+24.,distance)
    bank+=(23.-7.)*smooth(channel+24.,channel+75.,distance)
    blend=smooth(channel+75.,channel+180.,distance)
    carve=bank*(1-blend)+target*blend
    target=np.where(distance<channel+180.,target*(1-end_fade)+np.minimum(target,carve)*end_fade,target)
    # Preserve open-sea bathymetry and smoothly join the exact saved shore mesh.
    target=old*(1-smooth(-15,32,inland))+target*smooth(-15,32,inland)
    return old*(1-edge)+target*edge,edge

rows=[];seams={};changed_total=0
for record in intake['tiles']:
    source=R/record['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source));obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mesh=obj.data
    origin=record['local_origin'];saved=np.load(R/'captures/highcoast36-saved-inputs'/(record['name']+'.npz'))
    world=saved['vertices_world'].copy();old=world[:,1].copy()
    new,weight=sculpt_height(world[:,0],world[:,2],old)
    changed=np.abs(new-old)>1e-5
    if not np.any(changed):continue
    # Original saved objects use identity native transform; do not apply a
    # global coordinate deformation to a non-identity object by accident.
    assert np.max(np.abs(np.array(obj.matrix_world)-np.eye(4)))<1e-9
    for i,v in enumerate(mesh.vertices):v.co.z=float(new[i])
    mesh.update();mesh.calc_loop_triangles()
    world[:,1]=new
    attr=mesh.color_attributes.get('Palette');assert attr is not None and attr.domain=='CORNER'
    changed_faces=0
    for face in mesh.polygons:
        ids=list(face.vertices)
        if not any(changed[i] for i in ids):continue
        changed_faces+=1
        points=world[ids];center=points.mean(axis=0)
        n=np.cross(points[1]-points[0],points[2]-points[0]);n/=max(np.linalg.norm(n),1e-10)
        up=abs(n[1]);facing=np.dot(n,np.array([.4,.6,-.65]))
        grass=np.array([.40,.48,.285])*(.88+.12*max(facing,0))
        rock=np.array([.44,.455,.45])*(.82+.16*max(facing,0))
        steep=float(1-smooth(.48,.78,up))
        pigment=grass*(1-steep)+rock*steep
        snow=float(smooth(310,400,center[1]))*float(smooth(.32,.64,up))
        pigment=pigment*(1-snow)+np.array([.75,.79,.82])*snow
        if center[1]<5: pigment=np.array([.39,.43,.38])
        linear=np.where(pigment<=.04045,pigment/12.92,((pigment+.055)/1.055)**2.4)
        for loop in face.loop_indices:attr.data[loop].color=(*linear,1.)
    obj['sculpt_revision']='36a: authored coastal spines and tidal estuary'
    obj['source_sha256']=record['source_sha256']
    obj['boundary_policy']='Saved XZ/topology retained; shared global sculpt field; outer influence falls to zero'
    bpy.context.view_layer.objects.active=obj
    for o in bpy.context.scene.objects:o.select_set(o==obj)
    name=record['name'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
    triangles=np.asarray(saved['triangles'])
    np.savez_compressed(OUT/(name+'-mesh.npz'),vertices_world=world,triangles=triangles,changed_vertices=changed)
    # Exact native seam positions across all touched tiles, including unchanged
    # boundary coordinates, before Godot conversion/collision rounding.
    for xyz in world:
        localx=xyz[0]-origin[0];localz=xyz[2]-origin[2]
        if min(abs(localx),abs(localx-768),abs(localz),abs(localz-768))<.001:
            key=(round(float(xyz[0]),4),round(float(xyz[2]),4));seams.setdefault(key,[]).append(float(xyz[1]))
    rows.append(dict(name=name,origin=origin,source_sha256=record['source_sha256'],vertices=len(world),triangles=len(triangles),changed_vertices=int(changed.sum()),changed_faces=changed_faces,
                     max_raise_m=float((new-old).max()),max_lower_m=float((new-old).min()),world_bounds=[world.min(axis=0).tolist(),world.max(axis=0).tolist()],
                     blend_sha256=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()))
    changed_total+=int(changed.sum());print('36a SCULPTED',name,int(changed.sum()),flush=True)
seam_delta=max([max(v)-min(v) for v in seams.values() if len(v)>1] or [0.])
assert seam_delta<.002,seam_delta
report=dict(scope='Local saved-native terrain sculpt, same XZ vertices and topology. Authored spines/coastal shoulders/tidal inlet. No whole-world generator. Occupancy/actual collision and full visual acceptance require same-world assembly checks.',
            native_tiles=rows,changed_vertices=changed_total,shared_edge_max_delta_m=seam_delta,design_bounds=[[-3750,-4400],[-900,-2150]],ridge_controls=RIDGES,tidal_estuary_controls=RIVER,
            production_modified=False,visual_accepted=False)
(OUT/'model-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('36a HIGH COAST NATIVE READY',len(rows),changed_total,seam_delta,flush=True)
