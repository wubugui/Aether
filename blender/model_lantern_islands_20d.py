"""Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/lantern_islands_study_20d'
if OUT.exists():raise RuntimeError('Frozen study already exists')
OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
parts=[];reports=[]

def mat(name,rgb,metal=0,rough=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

rock=mat('Coast blue grey bedrock',(.043,.056,.066))
rockface=mat('Coast exposed fracture',(.070,.077,.080))
rockdark=mat('Coast tidal dark stone',(.028,.039,.046),rough=.62)
grass=mat('Coast short olive grass',(.050,.086,.018))
soil=mat('Coast grass soil edge',(.061,.066,.032))
plaster=mat('Keeper lime plaster',(.36,.32,.235))
stone=mat('Keeper sandstone foundations',(.195,.184,.158))
wood=mat('Keeper weathered oak',(.18,.10,.052))
roof=mat('Keeper terracotta tile',(.26,.105,.067))
roofedge=mat('Keeper darker roof seams',(.16,.064,.043))
metal=mat('Keeper dark forged bronze',(.135,.105,.072),metal=.35)
glass=mat('Keeper window glass',(.047,.073,.078),rough=.22)
dark=mat('Keeper chimney darkness',(.016,.019,.021))

def reset():
    global parts
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);parts=[]

def mesh(name,vertices,faces,material):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    data.materials.append(material);parts.append(obj)
    return obj

def box(name,center,size,material,rotation=0):
    x,y,z=size;cx,cy,cz=center
    verts=[(a*x/2,b*y/2,c*z/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    co,si=math.cos(rotation),math.sin(rotation)
    verts=[(cx+co*x-si*y,cy+si*x+co*y,cz+z) for x,y,z in verts]
    return mesh(name,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],material)

def beam(name,a,b,width,depth,material):
    a,b=Vector(a),Vector(b);axis=(b-a).normalized()
    u=axis.cross(Vector((0,0,1)))
    if u.length<.01:u=axis.cross(Vector((0,1,0)))
    u.normalize();v=axis.cross(u).normalized()
    verts=[p+u*x*width/2+v*y*depth/2 for p in [a,b] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    return mesh(name,verts,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],material)

def loft(name,rings,material):
    n=len(rings[0]);assert all(len(r)==n for r in rings)
    verts=[p for ring in rings for p in ring]
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    return mesh(name,verts,faces,material)

def freeze(name,scope):
    # Normalize and inspect the actual source mesh before its editable save.
    defects=[];volumes={}
    for obj in parts:
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
        if any(not e.is_manifold for e in bm.edges):defects.append([obj.name,'open/nonmanifold edge'])
        if any(f.calc_area()<1e-9 for f in bm.faces):defects.append([obj.name,'zero area'])
        volume=bm.calc_volume(signed=True);volumes[obj.name]=volume
        if volume<=0:defects.append([obj.name,'nonpositive signed volume'])
        bm.to_mesh(obj.data);bm.free();obj.data.update()
        obj['authoring_role']='Independent editable coastal scene component'
    report={'name':name,'scope':scope,'parts':len(parts),'vertices':sum(len(o.data.vertices) for o in parts),
            'polygons':sum(len(o.data.polygons) for o in parts),'native_closed_solid_check_passed':not defects,
            'defects':defects,'component_volumes_m3':volumes}
    bpy.context.scene['reference_images']='ref/1126.png;ref/1342.png;ref/1218.png'
    bpy.context.scene['scope']=scope
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    # Batch only the export copy by material, preserving all native components above.
    groups={}
    for o in parts:groups.setdefault(o.data.materials[0].name,[]).append(o)
    for material,objects in groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects)>1:bpy.ops.object.join()
        bpy.context.object.name=name+'_'+material
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=str(OUT/(name+'.glb')),export_format='GLB',use_selection=True,export_apply=True)
    report['export_mesh_nodes']=len(groups)
    report['source_sha256']=hashlib.sha256((OUT/(name+'.blend')).read_bytes()).hexdigest()
    report['glb_sha256']=hashlib.sha256((OUT/(name+'.glb')).read_bytes()).hexdigest()
    reports.append(report)
    if defects:raise RuntimeError('Native geometry rejected: '+str(defects))

# Hand-shaped coast outline: a long southern shoulder, two eastern notches,
# unequal northern headlands, and a broad western recess. Never a radial cone.
outline=[(-80,-20),(-74,-45),(-46,-63),(-24,-59),(-8,-50),(14,-59),(38,-47),(61,-40),(75,-21),(88,6),(71,19),(75,40),(48,47),(29,60),(1,48),(-22,53),(-52,38),(-71,13)]
rim_heights=[16,18,20,22,21,23,25,23,20,21,20,18,17,19,21,20,18,15]
shape8=[(-1,-.5),(-.4,-.9),(.6,-.8),(1,-.2),(.85,.55),(.2,1),(-.75,.7),(-1,.1)]

def block(name,center,scale,turn=0):
    cx,cy,cz=center;sx,sy,sz=scale;co,si=math.cos(turn),math.sin(turn)
    profiles=[(1.12,-.35,0,0),(1.0,.05,-.03,.01),(.81,.63,.13,-.07),(.38,1.0,-.21,.12)]
    rings=[]
    top_offsets=[-.18,.11,.00,-.12,.16,-.09,.04,-.18]
    for j,(r,h,ox,oy) in enumerate(profiles):
        ring=[]
        for i,(x,y) in enumerate(shape8):
            px=(x*r+ox)*sx;py=(y*r+oy)*sy
            ring.append((cx+co*px-si*py,cy+si*px+co*py,cz+(h+(top_offsets[i] if j>1 else 0))*sz))
        rings.append(ring)
    obj=loft(name,rings,rock)
    obj.data.materials.append(rockface);obj.data.materials.append(rockdark)
    for p in obj.data.polygons:
        if p.center.z<1.4:p.material_index=2
        elif p.normal.x<-.55 and p.normal.z<.6:p.material_index=1
    return obj

def inside(x,y,polygon):
    result=False;j=len(polygon)-1
    for i,(xi,yi) in enumerate(polygon):
        xj,yj=polygon[j]
        if (yi>y)!=(yj>y) and x<(xj-xi)*(y-yi)/(yj-yi)+xi:result=not result
        j=i
    return result

def island(name,sx,sy,plateau,variant):
    reset();coast=[]
    for i,(x,y) in enumerate(outline):
        dx=([0,5,-3,1,-7,0,3,0,-5,0,2,7,1,-5,0,3,4,-3][i] if variant==1 else ([3,-5,4,0,-2,5,0,-7,4,0,-4,0,8,0,-4,0,3,-3][i] if variant==2 else 0))
        coast.append(((x+dx)*sx,y*sy))
    top_scales=[.98,.92,.85,.79,.88,.90,.96,.83,.79,.72,.74,.80,.95,.98,.89,.82,.75,.79]
    boundary=[(x*top_scales[(i+variant*3)%18],y*top_scales[(i+variant*3)%18]) for i,(x,y) in enumerate(coast)]
    def ungraded(x,y):
        a,b=x/sx,y/sy
        return max(5.,plateau-.0025*a*a-.003*b*b+2.8*math.sin((a+18+variant*9)/32)*math.cos((b-5)/45))
    # Only small building pads are level; the rest remains a real sculpted slope.
    pads=([(-3,6,6.3,6.3,.25),(-22,-2,4.3,7.0,0),(19,-6,3.8,6.2,-.15)] if variant==0 else
          ([(0,2,6.3,6.3,-.12),(-15,-3,3.6,5.9,.08)] if variant==1 else [(1,1,6.3,6.3,.1),(9,-4,3.2,5.3,-.15)]))
    def height(x,y):
        value=ungraded(x,y)
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx-si*dy,si*dx+co*dy
            distance=max(abs(u)-wx,abs(v)-wy,0.)
            if distance<3.8:
                t=min(1.,distance/3.8);weight=1-t*t*(3-2*t)
                value=value*(1-weight)+ungraded(cx,cy)*weight
        return value
    coords=[Vector(p) for p in boundary]
    # A staggered terrain lattice provides coherent large facets, not random shards.
    spacing=9.*sx
    for row in range(-12,13):
        y=row*spacing*.866
        for col in range(-14,15):
            x=(col+.5*(row%2))*spacing
            if inside(x,y,boundary) and min((Vector((x,y))-p).length for p in coords[:18])>2.:
                coords.append(Vector((x,y)))
    for cx,cy,wx,wy,angle in pads:
        co,si=math.cos(angle),math.sin(angle)
        for u,v in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy),(0,0)]:
            x,y=cx+co*u+si*v,cy-si*u+co*v
            if inside(x,y,boundary):coords.append(Vector((x,y)))
    verts2,edges,triangles,original,_,_=delaunay_2d_cdt(coords,[],[list(range(18))],1,.00001)
    assert triangles and all(len(t)==3 for t in triangles)
    n=len(verts2);top=[(p.x,p.y,height(p.x,p.y)) for p in verts2]
    lower=[(x,y,z-.65) for x,y,z in top]
    edge_counts={}
    for triangle in triangles:
        for j in range(3):
            a,b=triangle[j],triangle[(j+1)%3];key=tuple(sorted((a,b)))
            edge_counts[key]=edge_counts.get(key,0)+1
    border=[edge for edge,count in edge_counts.items() if count==1]
    capfaces=[tuple(t) for t in triangles]+[tuple(i+n for i in reversed(t)) for t in triangles]
    capfaces.extend([(a,b,b+n,a+n) for a,b in border])
    cap=mesh(name+' sculpted grass terrain',top+lower,capfaces,grass);cap.data.materials.append(soil)
    for i,p in enumerate(cap.data.polygons):
        if i>=len(triangles):p.material_index=1
    # Side silhouette follows the same constrained boundary as the grass.
    # Nonplanar cliff quads are explicitly split into broad fracture planes.
    coreverts=[];corefaces=[]
    for level in range(3):
        for i,(x,y) in enumerate(coast):
            k=top_scales[(i+variant*3)%18]
            if level==0:point=(x*1.10,y*1.10,-9.)
            elif level==1:point=(x,y,1.0+(i%3)*.22)
            else:point=(x*(1+k)/2,y*(1+k)/2,height(boundary[i][0],boundary[i][1])*.48)
            coreverts.append(point)
    coreverts+=lower
    index={}
    for i,orig in enumerate(original):
        for source in orig:
            if source<18:index[source]=54+i
    assert len(index)==18
    corefaces.append(tuple(reversed(range(18))))
    for level in range(3):
        for i in range(18):
            j=(i+1)%18;a=level*18+i;b=level*18+j
            c=(level+1)*18+j if level<2 else index[j]
            d=(level+1)*18+i if level<2 else index[i]
            if (i+level)%2:corefaces.extend([(a,b,d),(b,c,d)])
            else:corefaces.extend([(a,b,c),(a,c,d)])
    corefaces.extend([tuple(54+i for i in tri) for tri in triangles])
    core=mesh(name+' faulted bedrock',coreverts,corefaces,rock)
    core.data.materials.append(rockface);core.data.materials.append(rockdark)
    for p in core.data.polygons:
        if p.center.z<2.:p.material_index=2
        elif p.normal.x<-.60 and p.normal.z<.35:p.material_index=1
    # Four unequal promontories replace the evenly spaced ring of eight round caps.
    for i,(pos,size,turn) in enumerate([
        ((-72,-31,0),(18,11,19),-.60),((70,-7,0),(11,25,13),.70),
        ((25,44,0),(25,10,10),-.25),((-47,34,0),(12,17,15),.35)]):
        x,y,z=pos;a,b,c=size
        block(name+' fractured headland %02d'%i,(x*sx,y*sy,z),(a*sx,b*sy,c*plateau/24),turn+variant*.25)
    for i,(x,y,a,b,h) in enumerate([(-84,-37,10,8,5),(-61,-61,12,8,6),(45,-60,10,7,4),(91,22,9,13,6),(38,58,13,8,5),(-60,48,10,9,4)]):
        block(name+' tidal shelf %02d'%i,(x*sx,y*sy,-.5),(a*sx,b*sy,h),i*.43)
    freeze(name,'Sculpted constrained terrain with small graded building pads, unequal grass tongues and connected faulted rock cliffs. No world or weather acceptance.')

island('island_a',1.,1.,24.,0)
island('island_b',.75,.66,18.,1)
island('island_c',.56,.54,14.,2)

for name,scale in [('reef_low',(12,8,8)),('reef_spire',(9,7,22)),('reef_ridge',(20,9,12))]:
    reset();block(name+' main fracture',(0,0,-1),scale,.15)
    block(name+' secondary ledge',(scale[0]*.6,scale[1]*.3,-1),(scale[0]*.55,scale[1]*.65,scale[2]*.48),-.4)
    freeze(name,'Independent closed sea-rock pair, with submerged bottom and asymmetric fractured shoulders.')

# Keeper architecture is retained byte-for-byte from the corrected 20c source.
prior=ROOT/'captures/lantern_islands_study_20c'
record=next(r for r in json.loads((prior/'model-report.json').read_text())['assets'] if r['name']=='keeper_house')
for extension in ['.blend','.glb']:shutil.copy2(prior/('keeper_house'+extension),OUT/('keeper_house'+extension))
reports.append(record)

report={'label':'20d','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'Local editable island/reef/keeper-house candidates for one continuous world. Native solidity is a technical gate only; GPU views and independent visual review required.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
