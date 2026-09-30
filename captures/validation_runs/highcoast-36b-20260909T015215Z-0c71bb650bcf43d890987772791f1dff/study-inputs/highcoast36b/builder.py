"""Sculpt saved terrain tiles using authored ridges and a connected tidal estuary."""
from pathlib import Path
import bpy,numpy as np,json,hashlib,shutil,math
R=Path(__file__).resolve().parents[1];OUT=R/'captures/highcoast_study_36b'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
intake=json.loads((R/'reviews/36-terrain-savedmesh-intake.json').read_text())
# Explicit sculpting controls in world X,Z, height above existing shore, width.
# Different spine heights and branches make connected masses, not isolated cones.
RIDGES=[
    [[-2520,-2460,35,220],[-2330,-2670,72,280],[-2070,-2880,145,330],[-1770,-2920,110,330]],
    [[-3110,-3680,65,280],[-2800,-3830,140,340],[-2380,-3950,285,420],[-2110,-4100,210,340]],
    [[-2650,-4140,100,250],[-2380,-3950,285,380],[-2050,-3820,190,340],[-1850,-3630,105,310]],
    [[-1730,-3570,95,320],[-1520,-3740,265,380],[-1330,-3910,325,340],[-1160,-4110,160,260]],
    [[-2710,-2730,34,130],[-2520,-2820,65,210],[-2280,-2830,105,220]],
]
RIVER=[[-3090,-3190,110],[-2840,-3200,98],[-2640,-3130,78],[-2450,-3220,74],[-2240,-3310,66],[-2030,-3240,62],[-1840,-3370,52],[-1600,-3330,45],[-1390,-3210,26]]
# Authored irregular rock shoulders. Each ring has a broad grass cap, a short
# sloped rim, and a low apron. These are edits to the continuous native mesh.
SHELVES=[
    (46,[[-2660,-2470],[-2500,-2420],[-2350,-2510],[-2400,-2610],[-2540,-2670],[-2690,-2600]]),
    (62,[[-2890,-2760],[-2740,-2690],[-2550,-2760],[-2500,-2880],[-2690,-2960],[-2870,-2890]]),
    (32,[[-2930,-3030],[-2750,-2970],[-2650,-3030],[-2740,-3120],[-2900,-3100]]),
    (54,[[-3220,-3420],[-3090,-3330],[-2910,-3370],[-2900,-3500],[-3090,-3550],[-3250,-3510]]),
    (79,[[-3400,-3760],[-3250,-3620],[-3070,-3690],[-3000,-3840],[-3200,-3890],[-3390,-3880]]),
    (42,[[-2290,-3030],[-2100,-2970],[-1950,-3100],[-2040,-3180],[-2240,-3150]]),
    (58,[[-2530,-3460],[-2350,-3390],[-2190,-3470],[-2250,-3590],[-2440,-3620]]),
]

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
def ring_distance(ring,x,z):
    inside=np.zeros(x.shape,dtype=bool);best=np.full(x.shape,np.inf)
    for a,b in zip(ring,ring[1:]+ring[:1]):
        dx=b[0]-a[0];dz=b[1]-a[1]
        t=np.clip(((x-a[0])*dx+(z-a[1])*dz)/(dx*dx+dz*dz),0,1)
        best=np.minimum(best,np.hypot(x-a[0]-t*dx,z-a[1]-t*dz))
        if abs(dz)>1e-9:
            inside^=((a[1]>z)!=(b[1]>z)) & (x<(b[0]-a[0])*(z-a[1])/dz+a[0])
    return np.where(inside,best,-best)

def sculpt_height(x,z,old):
    coast=-1900.+(z+1500.)*(2300./3500.)
    inland=x-coast
    edge=smooth(-3750,-3540,x)*(1-smooth(-1120,-900,x))*smooth(-4400,-4210,z)*(1-smooth(-2360,-2150,z))
    target=np.full(x.shape,14.)
    for ridge in RIDGES:
        distance,(height,width),t=nearest_line(ridge,x,z)
        profile=np.maximum(0.,1.-distance/width)**1.45
        target=np.maximum(target,14.+height*profile)
    # Low headlands leave broad valley space before the more distant spines.
    for height,ring in SHELVES:
        d=ring_distance(ring,x,z)
        apron=10.+(height-10.)*smooth(-60.,18.,d)
        target=np.maximum(target,apron)
    # The river continues through a broad low apron instead of jumping from
    # water to a 238m uphill wall in its final 150m.
    distance,(halfwidth,),t=nearest_line(RIVER,x,z)
    bed=-5.+3.*t
    bank=bed+(6.-bed)*smooth(halfwidth*.66,halfwidth+28.,distance)
    bank+=18.*smooth(halfwidth+55.,halfwidth+150.,distance)
    blend=smooth(halfwidth+155.,halfwidth+370.,distance)
    carve=bank*(1-blend)+target*blend
    end_fade=1-smooth(.82,1.,t)
    target=np.where(distance<halfwidth+370.,target*(1-end_fade)+np.minimum(target,carve)*end_fade,target)
    target=old*(1-smooth(-15,36,inland))+target*smooth(-15,36,inland)
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
        grass=np.array([.46,.54,.335])*(.88+.12*max(facing,0))
        rock=np.array([.49,.51,.505])*(.82+.16*max(facing,0))
        steep=float(1-smooth(.48,.78,up))
        pigment=grass*(1-steep)+rock*steep
        snow=float(smooth(310,400,center[1]))*float(smooth(.32,.64,up))
        pigment=pigment*(1-snow)+np.array([.75,.79,.82])*snow
        if center[1]<5: pigment=np.array([.39,.43,.38])
        linear=np.where(pigment<=.04045,pigment/12.92,((pigment+.055)/1.055)**2.4)
        for loop in face.loop_indices:attr.data[loop].color=(*linear,1.)
    obj['sculpt_revision']='36b: lower rock shoulders, recessed spines and broad estuary apron'
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
    changed_total+=int(changed.sum());print('36b SCULPTED',name,int(changed.sum()),flush=True)
seam_delta=max([max(v)-min(v) for v in seams.values() if len(v)>1] or [0.])
assert seam_delta<.002,seam_delta
report=dict(scope='Local saved-native terrain sculpt, same XZ vertices and topology. Authored spines/coastal shoulders/tidal inlet. No whole-world generator. Occupancy/actual collision and full visual acceptance require same-world assembly checks.',
            native_tiles=rows,changed_vertices=changed_total,shared_edge_max_delta_m=seam_delta,design_bounds=[[-3750,-4400],[-900,-2150]],ridge_controls=RIDGES,tidal_estuary_controls=RIVER,shoulder_controls=SHELVES,
            production_modified=False,visual_accepted=False)
(OUT/'model-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('36b HIGH COAST NATIVE READY',len(rows),changed_total,seam_delta,flush=True)
