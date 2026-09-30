"""Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/lantern_islands_study_20c'
if OUT.exists():raise RuntimeError('Frozen study already exists')
OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
parts=[];reports=[]

def mat(name,rgb,metal=0,rough=.8):
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    return m

rock=mat('Coast blue grey bedrock',(.118,.136,.148))
rockface=mat('Coast exposed fracture',(.165,.172,.170))
rockdark=mat('Coast tidal dark stone',(.070,.085,.093),rough=.62)
grass=mat('Coast short olive grass',(.150,.205,.072))
soil=mat('Coast grass soil edge',(.098,.107,.056))
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
    profiles=[(1.12,-.35,0,0),(1.0,.05,-.03,.01),(.83,.72,.05,-.04),(.53,1.0,-.10,.07)]
    rings=[]
    top_offsets=[-.10,.04,.00,-.05,.07,-.02,.02,-.08]
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

def island(name,sx,sy,plateau,variant):
    reset();coast=[]
    for i,(x,y) in enumerate(outline):
        # Distinct silhouettes rather than uniform scaled duplicate islands.
        dx=([0,5,-3,1,-7,0,3,0,-5,0,2,7,1,-5,0,3,4,-3][i] if variant==1 else ([3,-5,4,0,-2,5,0,-7,4,0,-4,0,8,0,-4,0,3,-3][i] if variant==2 else 0))
        coast.append(((x+dx)*sx,y*sy))
    heights=[plateau+(h-24)*.78 for h in rim_heights]
    rings=[]
    for level in range(4):
        ring=[]
        for i,(x,y) in enumerate(coast):
            if level==0:p=(x*1.11,y*1.11,-9.)
            elif level==1:p=(x,y,1.2+(i%3)*.22)
            elif level==2:p=(x*.84+2*sx,y*.84-2*sy,heights[i]*.57)
            else:p=(x*.68,y*.68,heights[i]-.15)
            ring.append(p)
        rings.append(ring)
    core=loft(name+' layered bedrock mass',rings,rock)
    core.data.materials.append(rockface);core.data.materials.append(rockdark)
    for p in core.data.polygons:
        if p.center.z<2:p.material_index=2
        elif p.normal.x<-.45:p.material_index=1
    # A thick, independently editable grass/soil crown follows the sloping rock rim.
    outer=[(x*.68,y*.68,heights[i]) for i,(x,y) in enumerate(coast)]
    inner=[(x*.39,y*.39,plateau) for x,y in coast]
    cap=loft(name+' thick grassy shoulder',[[ (x,y,z-.65) for x,y,z in outer],outer,inner],grass)
    cap.data.materials.append(soil)
    for p in cap.data.polygons:
        if abs(p.normal.z)<.5:p.material_index=1
    # Asymmetric buttresses break the regular course into geological headlands.
    for i,(pos,size,turn) in enumerate([
        ((-66,-28,1),(24,18,17),-.32),((-35,-50,2),(20,16,16),.22),((13,-49,1),(18,14,20),-.2),
        ((63,-26,1),(22,15,18),.48),((72,9,1),(16,22,15),.27),((44,39,1),(21,16,18),-.55),
        ((-17,43,1),(23,15,15),.14),((-61,21,1),(19,23,13),-.15)]):
        x,y,z=pos;a,b,c=size
        block(name+' coastal buttress %02d'%i,(x*sx,y*sy,z),(a*sx,b*sy,c*plateau/24),turn+variant*.12)
    for i,(x,y,a,b,h) in enumerate([(-84,-37,10,8,5),(-61,-61,12,8,6),(45,-60,10,7,4),(91,22,9,13,6),(38,58,13,8,5),(-60,48,10,9,4)]):
        block(name+' low tide shelf %02d'%i,(x*sx,y*sy,-.5),(a*sx,b*sy,h),i*.43)
    freeze(name,'Editable local island rock mass, thick grass crown and discrete coastal buttresses; no world or weather acceptance.')

# These already checked geological assets retain their exact native/export identity.
prior=ROOT/'captures/lantern_islands_study_20b'
for record in json.loads((prior/'model-report.json').read_text())['assets']:
    if record['name']=='keeper_house':continue
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
for side in [-1,1]:
    for row in range(7):
        lo,hi=row/7,(row+1)/7
        x0,x1=side*3.95*lo,side*3.95*hi
        z0,z1=6.85-2.65*lo,6.85-2.65*hi
        verts=[(x0,-5.55,z0),(x1,-5.55,z1),(x1,5.55,z1),(x0,5.55,z0)]
        loft('Keeper roof thick tile course %d %d'%(side,row),[[(x,y,z-.14) for x,y,z in verts],verts],roof)
        beam('Keeper roof horizontal lap %d %d'%(side,row),(x1,-5.55,z1+.025),(x1,5.55,z1+.025),.032,.045,roofedge)
    beam('Keeper eaves fascia '+str(side),(side*3.95,-5.6,4.15),(side*3.95,5.6,4.15),.20,.25,wood)
for i in range(11):
    beam('Keeper ridge cap segment '+str(i),(0,-5.55+i*1.01,6.89),(0,-4.56+i*1.01,6.89),.28,.22,roof)
for x in [-3.5,3.5]:
    for y in [-5.,5.]:
        for j in range(6):box('Keeper corner quoin',(x,y,.78+j*.55),(.60,.62,.32),stone)
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

report={'label':'20c','production_modified':False,'reference_images':['1126','1342','1218'],'assets':reports,'scope':'Local editable island/reef/keeper-house candidates for one continuous world. Native solidity is a technical gate only; GPU views and independent visual review required.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2))
print('LANTERN COAST KIT BUILT '+json.dumps({'assets':len(reports),'parts':sum(r['parts'] for r in reports),'all_native_solids_passed':all(r['native_closed_solid_check_passed'] for r in reports)}),flush=True)
