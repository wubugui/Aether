"""Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/lantern_islands_study_20j'
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
pathmat=mat('Coast weathered stone footpath',(.085,.072,.046))
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
    shoulders=([(-52,-38,20,9,6),(43,-32,18,10,8),(52,31,19,12,6),(-37,32,15,10,4)] if variant==0 else
               ([(-40,-31,18,10,5),(30,32,15,13,6),(36,-20,12,8,4)] if variant==1 else
                [(-27,-24,13,10,4),(23,-9,11,9,4),(-12,38,12,9,3)]))
    def ridge_value(x,y):
        a,b=x/sx,y/sy
        return sum(h*math.exp(-2.2*(((a-cx)/wx)**2+((b-cy)/wy)**2)) for cx,cy,wx,wy,h in shoulders)
    def ungraded(x,y):
        a,b=x/sx,y/sy
        added=ridge_value(x,y)
        if variant==0:
            return added+max(3.1,plateau+7.*math.exp(-((a+1)/19)**2-((b-8)/23)**2)-.0018*a*a-.002*b*b+.12*a-.06*b)
        if variant==1:
            return added+max(3.4,plateau+6.*math.exp(-((a-8)/24)**2-((b-20)/25)**2)-.0022*a*a-.0015*b*b+.09*b)
        return added+max(2.8,plateau+5.*math.exp(-((a+6)/18)**2-((b-5)/28)**2)-.0015*a*a-.0018*b*b-.055*a)
    # Only small building pads are level; the rest remains a real sculpted slope.
    pads=([(-3,6,6.3,6.3,.25),(-22,-2,4.3,7.0,0),(19,-6,3.8,6.2,-.15)] if variant==0 else
          ([(0,2,6.3,6.3,-.12),(-15,-3,3.6,5.9,.08)] if variant==1 else [(1,1,6.3,6.3,.1),(-12,-14,3.2,5.3,-.15)]))
    def pad_height(x,y):
        value=ungraded(x,y)
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx+si*dy,-si*dx+co*dy
            distance=max(abs(u)-wx,abs(v)-wy,0.)
            if distance<3.8:
                t=min(1.,distance/3.8);weight=1-t*t*(3-2*t)
                value=value*(1-weight)+ungraded(cx,cy)*weight
        return value
    routes=([
        [(-22,-8.15),(-21,-12),(-15,-12),(-9,-9),(0,-7),(6,0),(6,6),(1.0,9.0)],
        [(18.2,-11.25),(13,-14),(7,-12),(0,-7)],
        [(-21,-12),(-33,-18),(-44,-25),(-59,-34),(-69,-37)]] if variant==0 else
       ([ [(-14.60,-8.03),(-9,-11),(-2,-10),(5,-5),(7,0),(4.815,3.347)],
          [(-9,-11),(-19,-18),(-30,-27),(-41,-30)] ] if variant==1 else
        [ [(-12.66,-18.3),(-7,-20),(0,-15),(6,-9),(9,-2),(8,3),(5.4,3.36)] ]))
    # Longitudinal profiles interpolate from actual entry platforms. Each branch
    # uses its already-graded junction height; first/last 2 m remain level.
    profiles=[]
    def closest_profile(point,profile):
        route,cumulative,z0,z1=profile;best=None
        for i in range(len(route)-1):
            a,b=Vector(route[i]),Vector(route[i+1]);edge=b-a
            t=max(0.,min(1.,(point-a).dot(edge)/edge.length_squared))
            d=(point-a-edge*t).length;s=cumulative[i]+edge.length*t
            progress=max(0.,min(1.,(s-2.)/max(1.,cumulative[-1]-4.)))
            value=z0+(z1-z0)*progress
            if best is None or d<best[0]:best=(d,value)
        return best
    for route in routes:
        cumulative=[0.]
        for a,b in zip(route,route[1:]):cumulative.append(cumulative[-1]+(Vector(b)-Vector(a)).length)
        ends=[]
        for p in [route[0],route[-1]]:
            value=pad_height(*p)
            for prior in profiles:
                distance,joined=closest_profile(Vector(p),prior)
                if distance<.05:value=joined
            ends.append(value)
        profiles.append((route,cumulative,*ends))
    def height(x,y):
        value=pad_height(x,y);point=Vector((x,y))
        distance,grade=min((closest_profile(point,p) for p in profiles),key=lambda pair:pair[0])
        # Level crossfall over the full path and shoulders, fading into terrain.
        if distance<5.:
            t=max(0.,min(1.,(distance-2.0)/3.0));weight=1-t*t*(3-2*t)
            value=value*(1-weight)+grade*weight
        # Protect each actual structure platform, with a short smooth outer join.
        for cx,cy,wx,wy,angle in pads:
            co,si=math.cos(angle),math.sin(angle);dx,dy=x-cx,y-cy
            u,v=co*dx+si*dy,-si*dx+co*dy
            d=max(abs(u)-wx,abs(v)-wy,0.)
            if d<1.2:
                t=d/1.2;weight=1-t*t*(3-2*t)
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
    # Densely constrain only the narrow route corridor; the outer island keeps
    # broad facets. This captures real crossfall instead of bridging steep faces.
    for route in routes:
        for a,b in zip(route,route[1:]):
            a,b=Vector(a),Vector(b);edge=b-a;normal=Vector((-edge.y,edge.x)).normalized()
            steps=max(2,math.ceil(edge.length/1.2))
            for i in range(steps+1):
                center=a.lerp(b,i/steps)
                for offset in [-4.8,-2.05,-.95,0.,.95,2.05,4.8]:
                    p=center+normal*offset
                    if inside(p.x,p.y,boundary):coords.append(p)
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
    cap=mesh(name+' grass and exposed rock terrain',top+lower,capfaces,grass);cap.data.materials.append(soil);cap.data.materials.append(rockface)
    for i,p in enumerate(cap.data.polygons):
        if i>=len(triangles):p.material_index=1
        else:
            a,b=p.center.x/sx,p.center.y/sy
            exposure=min(((a-cx)/wx)**2+((b-cy)/wy)**2 for cx,cy,wx,wy,h in shoulders)
            # Material boundaries follow actual raised rock shoulders and steep faces.
            if exposure<.70 or p.normal.z<.72:p.material_index=2
    # Side silhouette follows the same constrained boundary as the grass.
    # Nonplanar cliff quads are explicitly split into broad fracture planes.
    coreverts=[];corefaces=[]
    for level in range(4):
        for i,(x,y) in enumerate(coast):
            k=top_scales[i]
            if level==0:point=(x*1.10,y*1.10,-9.)
            elif level==1:point=(x,y,1.0+(i%3)*.22)
            else:
                before=Vector(coast[(i-1)%count]);after=Vector(coast[(i+1)%count])
                direction=after-before;outward=Vector((direction.y,-direction.x)).normalized()
                t=.34 if level==2 else .76
                shift=([-.6,2.8,-1.7,.8,3.2,-1.1,.4][(i+variant)%7] if level==2 else [1.8,-1.2,2.6,-.7,.3,-2.1,1.1][(i+variant*2)%7])*sx
                p=Vector((x,y)).lerp(Vector(boundary[i]),t)+outward*shift
                h=height(boundary[i][0],boundary[i][1])
                fraction=(.28+.095*math.sin(i*.85+variant)) if level==2 else (.69+.095*math.sin(i*.65+1.2+variant))
                point=(p.x,p.y,max(1.7,h*fraction))
            coreverts.append(point)
    coreverts+=lower
    index={}
    for i,orig in enumerate(original):
        for source in orig:
            if source<count:index[source]=4*count+i
    assert len(index)==count
    corefaces.append(tuple(reversed(range(count))))
    for level in range(4):
        for i in range(count):
            j=(i+1)%count;a=level*count+i;b=level*count+j
            c=(level+1)*count+j if level<3 else index[j]
            d=(level+1)*count+i if level<3 else index[i]
            if (i+level)%2:corefaces.extend([(a,b,d),(b,c,d)])
            else:corefaces.extend([(a,b,c),(a,c,d)])
    corefaces.extend([tuple(4*count+i for i in tri) for tri in triangles])
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
    # The route surface is clipped against the existing terrain triangles, so it
    # follows their actual planes rather than an approximate analytic height.
    ribbons=[];width=1.7 if variant==0 else 1.35
    for route in routes:
        left=[];right=[]
        for i,point in enumerate(route):
            prior=Vector(route[max(0,i-1)]);following=Vector(route[min(len(route)-1,i+1)])
            tangent=(following-prior).normalized();normal=Vector((-tangent.y,tangent.x))
            left.append(Vector(point)+normal*width/2);right.append(Vector(point)-normal*width/2)
        ribbon=left+list(reversed(right))
        assert all(inside(p.x,p.y,boundary) for p in ribbon),'Path route crosses island boundary'
        ribbons.append(ribbon)
    pathcoords=[Vector(p) for p in verts2]
    constraints=list(edge_counts)
    loops=[]
    for ribbon in ribbons:
        ids=list(range(len(pathcoords),len(pathcoords)+len(ribbon)));pathcoords+=ribbon;loops.append(ids)
    pv,pe,pt,_,_,_=delaunay_2d_cdt(pathcoords,constraints,loops,1,.00001)
    selected=[]
    for tri in pt:
        center=sum((pv[i] for i in tri),Vector((0,0)))/len(tri)
        if any(inside(center.x,center.y,ribbon) for ribbon in ribbons):selected.append(tri)
    def surface_at(p):
        for tri in triangles:
            a,b,c=[Vector(top[i]) for i in tri]
            det=(b.y-c.y)*(a.x-c.x)+(c.x-b.x)*(a.y-c.y)
            if abs(det)<1e-12:continue
            u=((b.y-c.y)*(p.x-c.x)+(c.x-b.x)*(p.y-c.y))/det
            v=((c.y-a.y)*(p.x-c.x)+(a.x-c.x)*(p.y-c.y))/det;w=1-u-v
            if min(u,v,w)>-1e-4:return u*a.z+v*b.z+w*c.z
        raise RuntimeError('Path point outside actual terrain '+str(p))
    used=sorted(set(i for tri in selected for i in tri));lookup={i:j for j,i in enumerate(used)}
    pathverts=[(pv[i].x,pv[i].y,surface_at(pv[i])+.045) for i in used];pn=len(pathverts)
    pathfaces=[tuple(lookup[i] for i in tri) for tri in selected]
    pathcounts={}
    for tri in pathfaces:
        for i in range(3):
            edge=tuple(sorted((tri[i],tri[(i+1)%3])));pathcounts[edge]=pathcounts.get(edge,0)+1
    pathfaces+=[tuple(i+pn for i in reversed(tri)) for tri in list(pathfaces)]
    pathfaces+=[(a,b,b+pn,a+pn) for (a,b),nuse in pathcounts.items() if nuse==1]
    pathverts+=[(x,y,z-.35) for x,y,z in list(pathverts)]
    mesh(name+' terrain fitted keeper paths',pathverts,pathfaces,pathmat)
    bpy.context.scene['path_scope']='Detailed solid footpath surface on actual triangulated terrain; landing, treads and full walking validation incomplete.'
    bpy.context.scene['path_routes_blender_xy']=json.dumps(routes)
    freeze(name,'Inclined cliff fracture bands and exposed rock shoulders with actual graded route corridors preserving structure platforms. Visual/site acceptance pending.')

island('island_a',1.,1.,24.,0)
island('island_b',.75,.66,18.,1)
island('island_c',.56,.54,14.,2)
prior=ROOT/'captures/lantern_islands_study_20h'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name'].startswith('island_'):continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(record['name']+extension),OUT/(record['name']+extension))
    reports.append(record)
report={'label':'20j','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'Three remodeled islands with graded terrain-fitted paths; accepted keeper house and three reef models retained from20h. No world regeneration or scene acceptance.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
