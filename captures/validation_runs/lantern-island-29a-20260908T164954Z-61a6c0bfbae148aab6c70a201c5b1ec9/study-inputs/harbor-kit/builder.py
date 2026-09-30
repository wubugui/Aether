"""Editable coastal kit: sculpted rock islands, sea stacks and a detailed keeper house.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/harbor_kit_study_22b'
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


# Structural wood follows the existing keeper/lighthouse palette.
timber=[mat('Harbor oak plank '+str(i),c) for i,c in enumerate([(.135,.074,.035),(.175,.098,.046),(.21,.123,.059),(.155,.086,.041)])]
endgrain=mat('Harbor timber end grain',(.104,.056,.027))
rope_mat=mat('Harbor hemp lashings',(.24,.17,.09))
canvas=mat('Harbor weathered red canvas',(.235,.055,.030),rough=.95)
sailcloth=mat('Harbor flax sail',(.43,.37,.25),rough=.98)
lampglass=mat('Harbor lantern glass',(.25,.18,.07),rough=.22)
lampglass.node_tree.nodes.get('Principled BSDF').inputs['Alpha'].default_value=.34
lampglass.surface_render_method='DITHERED'
lampcore=mat('Harbor lantern flame',(.8,.33,.045))
lampcore.node_tree.nodes.get('Principled BSDF').inputs['Emission Color'].default_value=(1.,.38,.065,1)
lampcore.node_tree.nodes.get('Principled BSDF').inputs['Emission Strength'].default_value=.9

def cylinder(name,at,radius,depth,material,n=12):
    x,y,z=at
    rings=[[(x+radius*math.cos(i*math.tau/n),y+radius*math.sin(i*math.tau/n),z+h) for i in range(n)] for h in [-depth/2,depth/2]]
    return loft(name,rings,material)

def hoop(name,at,radius,width,material,n=16,thickness=.025):
    x,y,z=at;verts=[]
    for r,h in [(radius,-width/2),(radius,width/2),(radius-thickness,-width/2),(radius-thickness,width/2)]:
        verts.extend([(x+r*math.cos(i*math.tau/n),y+r*math.sin(i*math.tau/n),z+h) for i in range(n)])
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
    return mesh(name,verts,faces,material)

def cord(name,points,radius=.03):
    for i,(a,b) in enumerate(zip(points,points[1:])):beam(name+' span %02d'%i,a,b,radius*2,radius*2,rope_mat)

def pier(name,width,length):
    reset();deck=2.35;half=width/2
    # Every board is an editable, thick timber with two tiny nail heads.
    rows=math.ceil(length/.43);board_depth=length/rows
    for i in range(rows):
        y=-length/2+(i+.5)*board_depth
        box('Deck crossboard %02d'%i,(0,y,deck-.075),(width,board_depth-.018,.15),timber[i%4])
        for x in [-half+.32,half-.32]:cylinder('Flush deck nail %02d %s'%(i,x),(x,y,deck-.004),.018,.008,metal,6)
    for x in [-half+.28,0,half-.28]:box('Long continuous stringer '+str(x),(x,0,deck-.30),(.20,length+.2,.30),timber[0])
    bays=math.ceil(length/3.6)
    for j in range(bays+1):
        y=-length/2+.28+j*(length-.56)/bays
        for side in [-1,1]:
            x=side*(half-.22)
            cylinder('Foundation pile %s %02d'%(side,j),(x,y,-1.30),.18,8.2,timber[(j+1)%4],8)
            cylinder('Pile end cap %s %02d'%(side,j),(x,y,2.83),.187,.09,endgrain,8)
            hoop('Iron pile band %s %02d'%(side,j),(x,y,2.54),.192,.14,metal,8)
        box('Pile crosshead %02d'%j,(0,y,deck-.53),(width+.3,.28,.24),timber[1])
        beam('Cross bent left %02d'%j,(-half+.22,y,-.8),(half-.22,y,1.6),.18,.19,timber[0])
    for side in [-1,1]:
        x=side*(half+.02)
        for j in range(3):
            y=length/2-1-j*2.0
            box('Rear guard post %s %s'%(side,j),(x,y,2.83),(.15,.15,1.13),timber[1])
        for j in range(2):
            a=length/2-1-j*2.;b=a-2.
            cord('Sagging hand rope %s %s'%(side,j),[(x,a,3.25),(x,(a+b)/2,3.05),(x,b,3.25)],.035)
    for x,y in [(-half+.35,-length/2+.8),(half-.35,-length/2+.8)]:
        cylinder('Mooring bollard',(x,y,2.66),.13,.65,metal,10)
        box('Bollard horn',(x,y,2.89),(.48,.12,.11),metal)
    freeze(name,'Detailed piled timber pier, thick separate deck planks, cross-braced piles, iron fasteners, guard ropes and mooring hardware. Deck2.35m, pile bottom-5.4m. Sea-bottom anchoring is not yet surveyed.')

pier('timber_pier',4.4,16.)
pier('pier_landing',10.8,6.)

prior=ROOT/'captures/harbor_kit_study_22a'
for asset in json.loads((prior/'model-report.json').read_text(encoding='utf-8'))['assets']:
    if asset['name'] in ['timber_pier','pier_landing']:continue
    for extension in ['.blend','.glb']:shutil.copy2(prior/(asset['name']+extension),OUT/(asset['name']+extension))
    reports.append(asset)
(OUT/'model-report.json').write_text(json.dumps({'label':'22b','production_modified':False,'assets':reports,'scope':'Only two pier modules changed: deck support stringers raised1cm to contact plank underside; nail tops flush. Four other22a modules retained byte-identically. Site ramps and full scene remain incomplete.'},indent=2))
print('HARBOR KIT BUILT22b '+str(sum(r['parts'] for r in reports)),flush=True)
