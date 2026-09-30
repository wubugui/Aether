"""Local castle revision from its saved Blender source; no world generation.

Godot-world metres are used inside this asset. The previous instance's
anisotropic transform is baked into retained parts, then the replacement
castle instance uses unit scale at the original origin.
"""
from pathlib import Path
import ast, json, math, hashlib
import bpy, bmesh, numpy as np
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
OUT=R/'captures/crownreach_study_37a'
OUT.mkdir(exist_ok=False)
SOURCE=R/'blender/settlement_kit/castle.blend'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
original=[]
for obj in list(bpy.context.scene.objects):
    if obj.type=='MESH':
        pts=[obj.matrix_world@Vector(p) for p in obj.bound_box]
        original.append(dict(name=obj.name,vertices=len(obj.data.vertices),faces=len(obj.data.polygons),bounds=[list(map(min,zip(*pts))),list(map(max,zip(*pts)))]))
    else:bpy.data.objects.remove(obj,do_unlink=True)
assert len(original)>70, 'Expected saved named castle architecture'
library=bpy.data.collections.new('Crownreach - carved stone and town roofs 37a')
bpy.context.scene.collection.children.link(library)
material=bpy.data.materials.new('Pale limestone - matte palette 37a');material.use_nodes=True
color=material.node_tree.nodes.new('ShaderNodeVertexColor');color.layer_name='Palette'
bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.95
material.node_tree.links.new(color.outputs['Color'],bsdf.inputs['Base Color'])
parts=[]
tree=ast.parse((R/'blender/create_assets.py').read_text())
for node in tree.body:
    if isinstance(node,ast.FunctionDef) and node.name in ['bl','lin','rgb','finish','box','cone','rod','mesh','roof']:
        exec(compile(ast.Module(body=[node],type_ignores=[]),'<castle authoring helpers>','exec'),globals())
def name(obj,label):obj.name=label;return obj
def remove(obj):
    if obj in parts:parts.remove(obj)
    bpy.data.objects.remove(obj,do_unlink=True)
stone='d2cbb5';light='e0d9c5';shade='b8b5a4';roofcol='b9ac91';dark='676e70'
retained=[]
for obj in list(bpy.context.scene.objects):
    if obj.type!='MESH':continue
    if obj.name.startswith(('Courtyard house','Courtyard roof','Main keep','Keep pitched roof','East hall')):
        obj.data.transform(Matrix.Diagonal((1.2,.78,.52,1)))
        # Retain saved architecture, with a pale stone/roof palette.
        c=lin(rgb(roofcol if 'roof' in obj.name.lower() else stone))
        for a in obj.data.color_attributes:
            for v in a.data:v.color=(*c,1)
        obj.data.materials.clear();obj.data.materials.append(material)
        for col in list(obj.users_collection):col.objects.unlink(obj)
        library.objects.link(obj);parts.append(obj);retained.append(obj.name)
    else:remove(obj)

def prism(label,polygon,z0,z1,tint):
    n=len(polygon);pts=[(x,y,z) for z in (z0,z1) for x,y in polygon]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return name(mesh(pts,faces,tint),label)
def arch_shape(cx,bottom,width,height):
    r=width/2;spring=bottom+height-r
    return [(cx-r,bottom),(cx+r,bottom)]+[(cx+r*math.cos(a),spring+r*math.sin(a)) for a in np.linspace(0,math.pi,9)]
def carve(obj,cutter):
    bpy.context.view_layer.objects.active=obj
    mod=obj.modifiers.new('Actual recessed opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);remove(cutter)
def repaint(obj,tint):
    c=lin(rgb(tint))
    for a in list(obj.data.color_attributes):obj.data.color_attributes.remove(a)
    a=obj.data.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    for v in a.data:v.color=(*c,1)
    obj.data.color_attributes.active_color_index=0;obj.data.color_attributes.render_color_index=0
def ring_body(label,x,z,profile,tint,n=8):
    points=[]
    for y,r in profile:
        points += [(x+r*math.cos(a),y,z+r*math.sin(a)) for a in [math.pi/8+i*math.tau/n for i in range(n)]]
    faces=[tuple(reversed(range(n))),tuple(range((len(profile)-1)*n,len(profile)*n))]
    for k in range(len(profile)-1):
        faces += [(k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n)]
    return name(mesh(points,faces,tint),label)
def turn_y(obj,cx,cz,a):
    origin=Vector(bl((cx,0,cz)))
    # Godot positive Y rotation maps to Blender positive Z rotation.
    obj.data.transform(Matrix.Translation(origin)@Matrix.Rotation(a,4,'Z')@Matrix.Translation(-origin))
def recessed_window(body,cx,zface,bottom,width,height,label,angle=0,axis_z=0):
    poly=arch_shape(cx,bottom,width,height)
    cutter=prism(label+' cutter',poly,zface-.29,zface+.08,stone)
    if angle:turn_y(cutter,cx,axis_z,angle)
    carve(body,cutter)
    pane=prism(label+' inset',poly,zface-.275,zface-.245,dark)
    sill=name(box((cx,bottom-.065,zface-.015),(width+.18,.13,.24),light,.035),label+' sill')
    mull=name(box((cx,bottom+height*.4,zface-.225),(.06,height*.8,.04),'aeaa98'),label+' mullion')
    if angle:
        for o in [pane,sill,mull]:turn_y(o,cx,axis_z,angle)

# Six individually proportioned towers, rebuilt as carved stone masses.
towers=[(-24,-7.02,16.64,1.45,'West watchtower',False),(-14.4,3.12,12.48,1.35,'Gate tower',True),(-6,-3.12,19.24,1.72,'Keep spire',False),(4.8,-7.8,22.36,1.5,'High tower',False),(14.4,1.56,14.04,1.42,'East tower',False),(26.4,-1.56,10.92,1.18,'Outer turret',True)]
for x,z,h,r,label,flat in towers:
    body=ring_body(label+' carved shaft',x,z,[(-.75,r*1.13),(.42,r*1.13),(.75,r),(h-.65,r*.88),(h-.45,r*1.04),(h,r*1.04)],stone)
    for k,y in enumerate([h*.3,h*.57,h*.80]):
        for side,a in enumerate([0,math.pi/2,math.pi,math.pi*1.5]):
            # Shaft tapers gently; recess enters the actual face.
            rr=r*(1-.12*(y+.6)/(h-.65));face=z+rr*math.cos(math.pi/8)
            recessed_window(body,x,face,y,.42 if k<2 else .5,1.1,label+f' window {k}-{side}',a,z)
    repaint(body,stone)
    ring_body(label+' base course',x,z,[(.15,r*1.17),(.32,r*1.17),(.45,r*1.08)],shade)
    ring_body(label+' upper stringcourse',x,z,[(h*.67,r*.965),(h*.67+.16,r*.965)],light)
    if flat:
        ring_body(label+' parapet lower',x,z,[(h,r*1.06),(h+.6,r*1.06)],shade)
        # Solid short merlons surround an inset roof deck, readable from above.
        for j in range(8):
            a=j*math.tau/8
            name(box((x+math.cos(a)*r*.94,h+.94,z+math.sin(a)*r*.94),(.48,.72,.48),light,.035),label+f' merlon {j}')
        name(cone((x,h+.62,z),.06,r*.80,r*.80,'a5a693',8),label+' inset roof deck')
    else:
        ring_body(label+' overhanging roof',x,z,[(h+.05,r*1.18),(h+.32,r*1.18),(h+1.05,r*.88),(h+3.05,.10)],roofcol)
        name(rod((x,h+3,z),(x,h+3.6,z),.045,'8f8d7d'),label+' metal finial')

# Preserve the saved keep and houses, carving their existing wall geometry.
for obj in list(parts):
    if not (obj.name.startswith('Courtyard house') or obj.name in ['Main keep','East hall']):continue
    godot=[(v.co.x,v.co.z,-v.co.y) for v in obj.data.vertices]
    lo=np.min(godot,axis=0);hi=np.max(godot,axis=0);cx=(lo[0]+hi[0])/2
    w=hi[0]-lo[0];h=hi[1]-lo[1];front=hi[2]
    for side in [-1,1]:
        xx=cx+side*w*.25
        recessed_window(obj,xx,front,max(1.35,h*.50),.6 if w<8 else .85,min(1.3,h*.33),obj.name+f' front window {side}')
    # A real recessed doorway, plus a low stone threshold.
    cut=prism(obj.name+' door cut',arch_shape(cx,.05,.9,min(1.9,h*.74)),front-.35,front+.1,stone)
    carve(obj,cut)
    prism(obj.name+' recessed oak door',arch_shape(cx,.06,.9,min(1.9,h*.74)),front-.33,front-.28,'8e8774')
    name(box((cx,.12,front+.16),(1.2,.24,.5),shade,.045),obj.name+' doorstep')
    # Full-depth roof-edge cornice and masonry quoins, rather than painted strips.
    name(box((cx,h-.12,(lo[2]+hi[2])/2),(w+.15,.22,hi[2]-lo[2]+.15),light,.04),obj.name+' eave course')
    for xx in [lo[0]+.12,hi[0]-.12]:
        name(box((xx,h*.5,front+.035),(.24,h,.18),shade,.025),obj.name+' dressed corner')
    repaint(obj,stone)
    if obj.name.startswith('Courtyard house'):
        z=(lo[2]+hi[2])/2
        name(box((cx+w*.29,h+1.10,z-.3),(.5,1.5,.55),shade,.035),obj.name+' chimney')
        name(box((cx+w*.29,h+1.92,z-.3),(.67,.18,.7),light,.035),obj.name+' chimney cap')

# Solid buttresses along the keep's back and lateral wall.
for x in [-7.5,-3.5,.5]:
    prism('Keep rear buttress',[(x-.32,-.5),(x+.32,-.5),(x+.32,6.5),(x-.20,6.5)],-8.55,-7.05,shade)

# Low offset wall runs retain the existing overall footprint, with a real gate.
walls=[(-28,-.8,1.45,24.2,3.8),(28.5,-.4,1.35,20.5,3.25),(-8,-15.0,39.5,1.3,3.6),(21.2,-13.7,12.2,1.3,3.35),(-16.2,12.45,24.0,1.3,2.9),(16.0,11.70,24.0,1.3,2.65)]
for i,(x,z,w,d,h) in enumerate(walls):
    name(box((x,(h-.8)/2,z),(w,h+.8,d),stone,.045),f'Curtain {i} stone wall')
    name(box((x,h-.27,z),(w+.24,.28,d+.38),light,.035),f'Curtain {i} wall walk cap')
    n=max(2,int(max(w,d)/2.0))
    for j in range(n):
        q=(j/(n-1)-.5)*(max(w,d)-.8)
        name(box((x+(q if w>d else 0),h+.34,z+(q if d>w else 0)),(.74,.88,.72),stone,.045),f'Curtain {i} merlon {j}')

# Front gate: five-sided real tunnel crown and individual arch stones.
gate_z=12.35;gate_r=2.35;spring=2.3;outer=gate_r+.48
for side in [-1,1]:
    name(box((side*(gate_r+.26),1.1,gate_z),(.52,3.8,2.2),light,.06),'Gate dressed jamb')
    name(box((side*(gate_r+.26),2.23,gate_z),(.72,.18,2.4),shade,.025),'Gate impost')
for i in range(13):
    a=i*math.pi/13+.009;b=(i+1)*math.pi/13-.009
    poly=[(gate_r*math.cos(a),spring+gate_r*math.sin(a)),(outer*math.cos(a),spring+outer*math.sin(a)),(outer*math.cos(b),spring+outer*math.sin(b)),(gate_r*math.cos(b),spring+gate_r*math.sin(b))]
    prism(f'Gate arch voussoir {i:02}',poly,gate_z-1.1,gate_z+1.1,light if i%3 else stone)
for side in [-1,1]:
    x=side*3.55
    name(box((x,2.15,gate_z),(1.35,5.6,2.5),stone,.07),'Gatehouse pier')
    name(box((x,5.01,gate_z),(1.6,.22,2.7),light,.035),'Gatehouse cap')

# Individual inset courtyard paving slabs and foundation footings.
# Neither is a photographed plane; slabs have thickness and editable edges.
for iz in range(10):
    for ix in range(4):
        x=(ix-1.5)*1.13;z=3.0+iz*.94
        name(box((x,.69,z),(1.10,.12,.90),['c2bfaa','c9c5af','b9b9a5'][(ix+iz)%3],.025),f'Courtyard paving {iz:02}-{ix}')
for i,(x,z,w,d,h) in enumerate(walls):
    name(box((x,-.32,z),(w+.45,1.65,d+.45),shade,.06),f'Curtain {i} embedded foundation')

# Source provenance, saved editable parts and exact exported same-version mesh.
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:
    obj['authoring']='Saved-source local castle refinement 37a; complete 3D geometry'
    obj.select_set(False)
scene=bpy.context.scene
bpy.ops.object.camera_add(location=(82,-108,63));camera=bpy.context.object
camera.rotation_euler=(Vector((0,0,8))-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
bpy.ops.object.light_add(type='SUN');bpy.context.object.rotation_euler=(.6,-.5,-.6);bpy.context.object.data.energy=2
scene.world.color=(.3,.36,.4)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'castle.blend'))
bpy.ops.object.select_all(action='DESELECT')
for obj in parts:obj.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(OUT/'castle.glb'),export_format='GLB',use_selection=True,export_apply=True,export_vertex_color='ACTIVE')
report={'source':str(SOURCE),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_parts':original,'retained_saved_parts':retained,'parts':[],'instance_origin':[43.288,18.845,-282.521],'instance_scale':[1,1,1],'prior_scale_baked':[1.2,.52,.78],'scope':'Local castle asset only; terrain/roads/scatter unmodified pending actual integration occupancy checks.'}
for obj in parts:
    pts=[obj.matrix_world@v.co for v in obj.data.vertices]
    report['parts'].append({'name':obj.name,'vertices':len(obj.data.vertices),'polygons':len(obj.data.polygons),'bounds_blender':[list(map(min,zip(*pts))),list(map(max,zip(*pts)))]})
(OUT/'model-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'builder.py').write_text(Path(__file__).read_text(),encoding='utf-8')
print('CROWNREACH37A SAVED',len(parts),'editable parts',flush=True)
