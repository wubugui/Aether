"""Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/lantern_islands_study_20g'
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
    reset()
    # Explicit independent coastlines: a cut eastern inlet, a bent western bay,
    # and a narrow hooked northern island. These are designed geography.
    outlines=[
        [(-90,-35),(-80,-60),(-45,-70),(-14,-56),(8,-48),(28,-60),(48,-53),(75,-46),(86,-22),(61,-17),(36,-12),(30,-3),(40,3),(69,4),(95,19),(83,40),(61,52),(34,61),(7,52),(-12,64),(-40,54),(-62,35),(-78,16),(-88,-4)],
        [(-84,-45),(-57,-68),(-24,-61),(2,-48),(33,-53),(62,-38),(70,-12),(52,9),(61,36),(38,63),(3,74),(-22,57),(-29,30),(-18,17),(-28,5),(-50,9),(-65,29),(-79,19),(-70,-8)],
        [(-58,-62),(-30,-73),(-4,-54),(25,-44),(51,-19),(45,1),(65,23),(49,43),(21,48),(10,67),(-12,73),(-27,49),(-11,28),(-4,15),(-19,8),(-48,26),(-66,10),(-74,-18)]
    ]
    coast=[(x*sx,y*sy) for x,y in outlines[variant]];count=len(coast)
    # Preserve concave mouth vertices rather than closing them with a radial cap.
    top_scales=[.93 if variant==0 and i in range(8,15) else (.94 if i%5 in (0,1) else .86) for i in range(count)]
    boundary=[(x*top_scales[i],y*top_scales[i]) for i,(x,y) in enumerate(coast)]
    def ungraded(x,y):
        a,b=x/sx,y/sy
        if variant==0:
            return max(3.1,plateau+7.*math.exp(-((a+1)/19)**2-((b-8)/23)**2)-.0018*a*a-.002*b*b+.12*a-.06*b)
        if variant==1:
            return max(3.4,plateau+6.*math.exp(-((a-8)/24)**2-((b-20)/25)**2)-.0022*a*a-.0015*b*b+.09*b)
        return max(2.8,plateau+5.*math.exp(-((a+6)/18)**2-((b-5)/28)**2)-.0015*a*a-.0018*b*b-.055*a)
    # Only small building pads are level; the rest remains a real sculpted slope.
    pads=([(-3,6,6.3,6.3,.25),(-22,-2,4.3,7.0,0),(19,-6,3.8,6.2,-.15)] if variant==0 else
          ([(0,2,6.3,6.3,-.12),(-15,-3,3.6,5.9,.08)] if variant==1 else [(1,1,6.3,6.3,.1),(-12,-14,3.2,5.3,-.15)]))
    def height(x,y):
        value=ungraded(x,y)
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx+si*dy,-si*dx+co*dy
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
            if inside(x,y,boundary) and min((Vector((x,y))-p).length for p in coords[:count])>2.:
                coords.append(Vector((x,y)))
    for cx,cy,wx,wy,angle in pads:
        co,si=math.cos(angle),math.sin(angle)
        for u,v in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy),(0,0)]:
            x,y=cx+co*u-si*v,cy+si*u+co*v
            if inside(x,y,boundary):coords.append(Vector((x,y)))
    verts2,edges,triangles,original,_,_=delaunay_2d_cdt(coords,[],[list(range(count))],1,.00001)
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
            k=top_scales[i]
            if level==0:point=(x*1.10,y*1.10,-9.)
            elif level==1:point=(x,y,1.0+(i%3)*.22)
            else:point=(x*(1+k)/2,y*(1+k)/2,height(boundary[i][0],boundary[i][1])*.48)
            coreverts.append(point)
    coreverts+=lower
    index={}
    for i,orig in enumerate(original):
        for source in orig:
            if source<count:index[source]=3*count+i
    assert len(index)==count
    corefaces.append(tuple(reversed(range(count))))
    for level in range(3):
        for i in range(count):
            j=(i+1)%count;a=level*count+i;b=level*count+j
            c=(level+1)*count+j if level<2 else index[j]
            d=(level+1)*count+i if level<2 else index[i]
            if (i+level)%2:corefaces.extend([(a,b,d),(b,c,d)])
            else:corefaces.extend([(a,b,c),(a,c,d)])
    corefaces.extend([tuple(3*count+i for i in tri) for tri in triangles])
    core=mesh(name+' faulted bedrock',coreverts,corefaces,rock)
    core.data.materials.append(rockface);core.data.materials.append(rockdark)
    for p in core.data.polygons:
        if p.center.z<2.:p.material_index=2
        elif p.normal.x<-.60 and p.normal.z<.35:p.material_index=1
    # Three distinct outcrops belong to the high eastern cliff, leaving the west
    # low shore and the actual concave inlet unobstructed.
    headlands=([
        ((66,-37,0),(13,16,20),-.45),((76,33,0),(12,17,24),.2),((27,48,0),(22,10,14),-.35)] if variant==0 else
        ([((45,45,0),(17,12,20),.6),((57,-27,0),(9,20,13),-.4)] if variant==1 else
         [((-50,-36,0),(10,18,15),.3),((40,31,0),(17,10,11),-.6)]))
    for i,(pos,size,turn) in enumerate(headlands):
        x,y,z=pos;a,b,c=size
        block(name+' cliff outcrop %02d'%i,(x*sx,y*sy,z),(a*sx,b*sy,c*plateau/24),turn)
    shelves=([(-86,-45,13,8,3.5),(-67,-66,15,10,4),(11,-55,15,7,4),(91,34,10,9,6),(-60,40,10,12,3)] if variant==0 else
             ([(-66,-55,10,9,4),(61,-28,10,13,5),(35,65,11,9,5),(-78,19,8,11,4)] if variant==1 else
              [(-62,-49,10,8,4),(42,-27,10,8,4),(49,40,13,8,5),(-22,62,9,8,4)]))
    for i,(x,y,a,b,h) in enumerate(shelves):
        block(name+' low shore ledge %02d'%i,(x*sx,y*sy,-.5),(a*sx,b*sy,h),i*.43)
    freeze(name,'Distinct concave coastline with an actual open inlet, asymmetric high cliff and low shore, locally graded building pads and sculpted slopes. No world or weather acceptance.')

# Rebuild only the C island: its former house footprint crossed the east cliff.
island('island_c',.56,.54,14.,2)
prior=ROOT/'captures/lantern_islands_study_20e'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name'] in ['island_c','keeper_house']:continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)

reset()
box('Keeper broad masonry footing',(0,0,-.15),(7.8,10.8,1.),stone)
box('Keeper raised floor',(0,0,.42),(7.1,10.1,.28),wood)

def wall(name,origin,tangent,normal,length,height,openings):
    origin,tangent,normal=Vector(origin),Vector(tangent),Vector(normal)
    xs=sorted(set([-length/2,length/2]+[v for a,b,c,d,kind in openings for v in [a,b]]))
    zs=sorted(set([.5,height]+[v for a,b,c,d,kind in openings for v in [c,d]]))
    filled={}
    for i in range(len(xs)-1):
        for j in range(len(zs)-1):
            u,z=(xs[i]+xs[i+1])/2,(zs[j]+zs[j+1])/2
            filled[i,j]=not any(a<u<b and c<z<d for a,b,c,d,kind in openings)
    verts=[];faces=[];lookup={}
    def vertex(u,z,depth):
        p=origin+tangent*u+normal*depth+Vector((0,0,z));key=tuple(round(v,6) for v in p)
        if key not in lookup:lookup[key]=len(verts);verts.append(p)
        return lookup[key]
    for (i,j),present in filled.items():
        if not present:continue
        a,b=xs[i:i+2];c,d=zs[j:j+2]
        front=[vertex(u,z,.22) for u,z in [(a,c),(b,c),(b,d),(a,d)]]
        back=[vertex(u,z,-.22) for u,z in [(a,c),(b,c),(b,d),(a,d)]]
        faces.extend([tuple(front),tuple(reversed(back))])
        for edge,neighbor in enumerate([(i,j-1),(i+1,j),(i,j+1),(i-1,j)]):
            if not filled.get(neighbor,False):faces.append((front[edge],back[edge],back[(edge+1)%4],front[(edge+1)%4]))
    mesh(name+' solid cut masonry',verts,faces,plaster)
    for k,(a,b,c,d,kind) in enumerate(openings):
        def p(u,z,depth=.25):return origin+tangent*u+normal*depth+Vector((0,0,z))
        border=.10
        for label,u1,z1,u2,z2 in [('sill',a-border,c,b+border,c),('lintel',a-border,d,b+border,d),('left',a,c,a,d),('right',b,c,b,d)]:
            beam(name+' '+kind+' '+str(k)+' '+label,p(u1,z1),p(u2,z2),.16,.18,wood)
        if kind=='window':
            pane=[p(u,z,depth) for depth in [.025,.06] for u,z in [(a,c),(b,c),(b,d),(a,d)]]
            mesh(name+' window glazing '+str(k),pane,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],glass)
            beam(name+' window vertical mullion '+str(k),p((a+b)/2,c,.28),p((a+b)/2,d,.28),.06,.08,wood)
            beam(name+' window crossbar '+str(k),p(a,(c+d)/2,.28),p(b,(c+d)/2,.28),.06,.08,wood)
            beam(name+' stone sill '+str(k),p(a-.18,c-.13,.25),p(b+.18,c-.13,.25),.30,.20,stone)
        else:
            for q in range(6):
                u=a+(b-a)*(q+.5)/6
                beam(name+' door oak board '+str(q),p(u,c,.04),p(u,d,.04),(b-a)/6-.012,.10,wood)
            for z in [c+.45,d-.45]:beam(name+' door hinge strap',p(a+.1,z,.14),p(b-.1,z,.14),.06,.055,metal)
            beam(name+' door handle',p(b-.25,c+1.0,.22),p(b-.25,c+1.25,.22),.04,.05,metal)

wall('Keeper front',(0,-5,0),(1,0,0),(0,-1,0),7,4.2,[(-.8,.8,.5,2.9,'door'),(-2.7,-1.5,1.5,2.9,'window'),(1.5,2.7,1.5,2.9,'window')])
wall('Keeper back',(0,5,0),(-1,0,0),(0,1,0),7,4.2,[(-2.5,-1.1,1.5,2.9,'window'),(1.1,2.5,1.5,2.9,'window')])
wall('Keeper east',(3.5,0,0),(0,1,0),(1,0,0),10,4.2,[(-3.2,-1.8,1.5,2.9,'window'),(1.8,3.2,1.5,2.9,'window')])
wall('Keeper west',(-3.5,0,0),(0,-1,0),(-1,0,0),10,4.2,[(-3.2,-1.8,1.5,2.9,'window'),(1.8,3.2,1.5,2.9,'window')])
for y in [-5,5]:
    loft('Keeper thick gable '+str(y),[[(-3.5,y-.22,4.2),(3.5,y-.22,4.2),(0,y-.22,6.65)],[(-3.5,y+.22,4.2),(3.5,y+.22,4.2),(0,y+.22,6.65)]],plaster)
    beam('Keeper gable left verge',(-3.85,y,4.15),(0,y,6.8),.18,.18,wood)
    beam('Keeper gable right verge',(0,y,6.8),(3.85,y,4.15),.18,.18,wood)
# Staggered short tiles: true separate thickness and a shallow raised crown.
# Tile joints break between courses instead of drawing eleven-metre dark lines.
for side in [-1,1]:
    for row in range(7):
        lo,hi=row/7,min(1.,(row+1)/7+.007)
        x0,x1=side*3.95*lo,side*3.95*hi
        z0,z1=6.85-2.65*lo,6.85-2.65*hi
        pitch=.84;offset=.42 if row%2 else 0
        for col in range(-1,15):
            ya=max(-5.55,-5.55+col*pitch+offset+.006)
            yb=min(5.55,-5.55+(col+1)*pitch+offset-.006)
            if yb-ya<.10:continue
            ym=(ya+yb)/2
            vertices=[(x0,ya,z0),(x1,ya,z1),(x1,ym,z1+.035),(x1,yb,z1),(x0,yb,z0),(x0,ym,z0+.035)]
            lower=[(x,y,z-.095) for x,y,z in vertices]
            faces=[(0,5,2,1),(5,4,3,2),(6,7,8,11),(11,8,9,10)]
            faces.extend([(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)])
            mesh('Keeper staggered roof tile %d %d %d'%(side,row,col),lower+vertices,faces,roof)
    beam('Keeper eaves fascia '+str(side),(side*3.95,-5.6,4.15),(side*3.95,5.6,4.15),.20,.25,wood)
for i in range(11):
    ya=-5.55+i*1.01;yb=min(5.55,ya+1.0)
    cross=[(-.19,6.78),(.19,6.78),(.18,6.89),(0,7.02),(-.18,6.89)]
    loft('Keeper shaped ridge cap '+str(i),[[(x,ya,z) for x,z in cross],[(x,yb,z) for x,z in cross]],roof)
quoin=mat('Keeper warm recessed corner stone',(.16,.135,.100))
for x in [-3.5,3.5]:
    for y in [-5.,5.]:
        for j in range(6):box('Keeper corner quoin',(x,y,.78+j*.55),(.48 if j%2 else .55,.55 if j%2 else .48,.29),quoin)
for i,(depth,height) in enumerate([(1.1,.18),(.65,.35)]):
    box('Keeper entrance stone step '+str(i),(0,-5.3-depth/2,height/2),(2.0,depth,height),stone)
for x in [-1.3,1.3]:beam('Keeper porch oak post '+str(x),(x,-6.55,.0),(x,-6.55,2.9),.17,.17,wood)
beam('Keeper porch lintel',(-1.45,-6.55,2.85),(1.45,-6.55,2.85),.20,.24,wood)
loft('Keeper porch solid pitched canopy',[[(-1.6,-6.8,2.9),(1.6,-6.8,2.9),(1.6,-4.85,3.5),(-1.6,-4.85,3.5)], [(-1.6,-6.8,3.05),(1.6,-6.8,3.05),(1.6,-4.85,3.65),(-1.6,-4.85,3.65)]],roof)
for x in [-1.3,1.3]:beam('Keeper porch knee brace',(x,-6.55,2.25),(x,-5.95,3.05),.11,.13,wood)
for x in [-2.4,-1.6]:box('Keeper chimney side',(x,2.4,6.15),(.18,.94,3.0),stone)
for y in [1.95,2.85]:box('Keeper chimney cross wall',(-2.,y,6.15),(.98,.18,3.0),stone)
box('Keeper chimney dark recessed flue',(-2,2.4,7.15),(.62,.62,.08),dark)
for a,b in [((-2.6,1.85,7.75),(-1.4,1.85,7.75)),((-2.6,2.95,7.75),(-1.4,2.95,7.75)),((-2.55,1.85,7.75),(-2.55,2.95,7.75)),((-1.45,1.85,7.75),(-1.45,2.95,7.75))]:beam('Keeper chimney coping',a,b,.20,.20,stone)
freeze('keeper_house','Detailed independent keeper house with closed wall reveals, true window/door openings, individual roof courses, porch joinery, quoins and open chimney; no furnished cabin or night lighting claim.')

report={'label':'20g','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'C island house pad repair and detailed keeper roof; five prior landforms byte-identical. Local candidates, not visual or scene acceptance.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
