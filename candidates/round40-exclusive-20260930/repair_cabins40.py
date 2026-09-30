"""Local Blender repairs to retained native assets; no world regeneration."""
import bpy, math, json
from pathlib import Path

base=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(base/'source-assets/sky_kit_baseline.blend'))
material=bpy.data.materials.get('Palette_38')
added=[]

def mesh(name,verts,faces,collection):
    data=bpy.data.meshes.new(name)
    data.from_pydata(verts,[],faces); data.update()
    colors=data.color_attributes.new('Col','BYTE_COLOR','CORNER')
    # Dark wood behind the exposed boards leaves a seam but prevents sky holes.
    colorspace=lambda v: ((v+.055)/1.055)**2.4 if v>.04045 else v/12.92
    color=tuple(colorspace(v) for v in [.26,.155,.085])+(1.,)
    for loop in colors.data: loop.color=color
    data.materials.append(material)
    obj=bpy.data.objects.new(name,data); collection.objects.link(obj); added.append(name)
    return obj

def box(name,size,center,collection):
    verts=[(center[0]+x*size[0]/2,center[1]+y*size[1]/2,center[2]+z*size[2]/2) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    return mesh(name,verts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],collection)

def window_lining(asset,x,D,H,cy,cz,radius,sides):
    collection=bpy.data.collections[asset]
    # Radial polygon annulus with exact outer rectangle corner coverage.
    offset=math.pi/sides if sides==8 else 0
    angles=[(2*math.pi*i/sides+offset)%(2*math.pi) for i in range(sides)]
    angles.extend(math.atan2(z-cz,y-cy)%(2*math.pi) for y,z in [(-D/2,0),(D/2,0),(D/2,H),(-D/2,H)])
    angles=sorted(set(angles)); inner=[]; outer=[]
    polygon=[(cy+radius*math.cos(2*math.pi*i/sides+offset),cz+radius*math.sin(2*math.pi*i/sides+offset)) for i in range(sides)]
    for angle in angles:
        dy,dz=math.cos(angle),math.sin(angle)
        distances=[]
        for i in range(sides):
            y0,z0=polygon[i];y1,z1=polygon[(i+1)%sides]
            sy,sz=y1-y0,z1-z0
            determinant=dy*sz-dz*sy
            if abs(determinant)<1e-9:continue
            t=((y0-cy)*sz-(z0-cz)*sy)/determinant
            u=((y0-cy)*dz-(z0-cz)*dy)/determinant
            if t>=0 and -1e-7<=u<=1+1e-7:distances.append(t)
        ri=min(distances)
        bounds=[]
        if dy>1e-9:bounds.append((D/2-cy)/dy)
        if dy<-1e-9:bounds.append((-D/2-cy)/dy)
        if dz>1e-9:bounds.append((H-cz)/dz)
        if dz<-1e-9:bounds.append(-cz/dz)
        ro=min(bounds)
        inner.append((cy+ri*dy,cz+ri*dz));outer.append((cy+ro*dy,cz+ro*dz))
    n=len(angles);verts=[]
    for xx in [x-.025,x+.025]:
        verts.extend((xx,y,z) for y,z in inner+outer)
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    mesh(asset+'_window_wall_lining40',verts,faces,collection)

for asset,W,D,H,side,cy,cz,radius,sides in [('cabin_a',6.,4.4,2.9,-1,.1,1.65,.99,8),('cabin_b',6.2,4.6,3.,1,.2,1.7,.96,16)]:
    collection=bpy.data.collections[asset]
    box(asset+'_floor_lining40',(W+.1,D+.1,.10),(0,0,-.075),collection)
    box(asset+'_ceiling_lining40',(W+.16,D+.16,.05),(0,0,H+.105),collection)
    box(asset+'_solid_wall_lining40',(.05,D+.1,H+.1),(-side*(W/2+.06),0,H/2),collection)
    for s in [-1,1]:box(asset+f'_end_wall_lining40_{s}',(W+.1,.05,H+.1),(0,s*(D/2+.06),H/2),collection)
    window_lining(asset,side*(W/2+.06),D+.1,H+.05,cy,cz,radius,sides)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.all_objects:obj.select_set(True)
    out=base/'project/assets/cabins40';out.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(out/(asset+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=str(base/'source-assets/cabins40.blend'))
(base/'evidence/blender-cabin-repair.json').write_text(json.dumps({'added_native_meshes':added,'scope':'Thin dark wood backing with genuine open window annulus, retaining all original parts; floor/ceiling/closed walls sealed.'},indent=2),encoding='utf8')
print('CABINS40 SAVED',len(added))
