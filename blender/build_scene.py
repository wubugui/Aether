"""Blender 4.5 authoring, mesh cleanup, native detail modeling, GLB export.
Run: blender --background --python blender/build_scene.py
"""
from pathlib import Path
import bpy, bmesh, numpy as np, json, math
from mathutils import Vector, Matrix

ROOT=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    if collection.name!='Collection':bpy.data.collections.remove(collection)

def linear(rgb):
    a=np.asarray(rgb)
    return np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)

def color_hex(s):return np.array([int(s[i:i+2],16)/255 for i in (0,2,4)])
def bl(p):return (p[0],-p[2],p[1])
SUN=Vector((-.48,-.30,.82)).normalized()

terrain_material=bpy.data.materials.new('Landscape UV color study')
terrain_material.use_nodes=True
terrain_nodes=terrain_material.node_tree.nodes;terrain_nodes.clear()
terrain_image=bpy.data.images.load(str(ROOT/'reference/occluded_color_reference.png'))
image_node=terrain_nodes.new('ShaderNodeTexImage');image_node.image=terrain_image
terrain_emission=terrain_nodes.new('ShaderNodeEmission')
terrain_output=terrain_nodes.new('ShaderNodeOutputMaterial')
terrain_material.node_tree.links.new(image_node.outputs['Color'],terrain_emission.inputs['Color'])
terrain_material.node_tree.links.new(terrain_emission.outputs[0],terrain_output.inputs['Surface'])
terrain_material['description']='Stable UV surface material on modeled 3D terrain, not a screen image.'

def landscape_uv(mesh):
    uv=mesh.uv_layers.new(name='LandscapeUV')
    angle=math.radians(-3.5);cos=math.cos(angle);sin=math.sin(angle)
    focal=941/(2*math.tan(math.radians(25)))
    for loop in mesh.loops:
        v=mesh.vertices[loop.vertex_index].co
        x=v.x;y=v.z-145;z=-v.y-250
        cy=cos*y+sin*z;cz=-sin*y+cos*z
        u=.5+(x/-cz)*focal/1672;vv=.5+(cy/-cz)*focal/941
        uv.data[loop.index].uv=(u,vv)

palette=bpy.data.materials.new('Hand-painted vertex palette')
palette.use_nodes=True
nt=palette.node_tree;nt.nodes.clear()
col=nt.nodes.new('ShaderNodeVertexColor');col.layer_name='Palette'
out=nt.nodes.new('ShaderNodeOutputMaterial');out.location=(350,0)
em=nt.nodes.new('ShaderNodeEmission');em.location=(160,0)
nt.links.new(col.outputs['Color'],em.inputs['Color']);nt.links.new(em.outputs[0],out.inputs['Surface'])
palette['description']='Per-corner colors on real geometry. No world image textures.'

groups={};roots={}
for name in ['Landscape','Airship','Propeller']:
    collection=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(collection)
    root=bpy.data.objects.new(name,None);collection.objects.link(root)
    groups[name]=collection;roots[name]=root

def into_group(obj,group):
    for c in list(obj.users_collection):c.objects.unlink(obj)
    groups[group].objects.link(obj);obj.parent=roots[group]

def assign_colors(obj,colors=None,base=None,ambient=.67):
    mesh=obj.data
    attr=mesh.color_attributes.get('Palette') or mesh.color_attributes.new(name='Palette',type='FLOAT_COLOR',domain='CORNER')
    if colors is not None:
        rgba=np.asarray(colors,dtype=np.float32).copy();rgba[:,:3]=linear(rgba[:,:3])
        attr.data.foreach_set('color',rgba.ravel())
    else:
        values=[]
        for poly in mesh.polygons:
            light=max(0,poly.normal.dot(SUN));c=np.clip(np.array(base)*(ambient+(1-ambient)*light),0,1)
            values.extend([np.r_[linear(c),1]]*len(poly.loop_indices))
        attr.data.foreach_set('color',np.array(values,np.float32).ravel())
    mesh.color_attributes.active_color_index=0
    mesh.color_attributes.render_color_index=0
    mesh.materials.clear();mesh.materials.append(palette)

control=np.load(ROOT/'blender/control_meshes.npz')
metadata=json.loads(str(control['metadata']))
for item in metadata:
    if item['name']=='Envelope':continue
    p=control[item['key']+'_p'].copy()
    colors=control[item['key']+'_c'].copy()
    if item['name']=='Rigging':
        centers=p.reshape(-1,3,3).mean(axis=1)
        keep=~((centers[:,1]>-1.48)&(centers[:,1]<2.65)&(np.abs(centers[:,0])>1.5))
        keep&=~((centers[:,0]>-.84)&(centers[:,0]<-.44)&(centers[:,1]>.02)&(centers[:,1]<.66))
        p=p.reshape(-1,3,3)[keep].reshape(-1,3)
        colors=colors.reshape(-1,3,4)[keep].reshape(-1,4)
    if item['name']=='Gondola':colors[:,:3]*=.82
    if item['name']=='Gondola':
        faces=p.reshape(-1,3,3)
        centers=faces.mean(axis=1)
        cabin_faces=(faces[:,:,1].max(axis=1)>-1.45)&(centers[:,0]>-1.2)&(centers[:,0]<2.05)
        cabin=np.repeat(cabin_faces,3)
        hull=(p[:,1]<-1.6)&~cabin
        p[hull,1]=-1.6+(p[hull,1]+1.6)*1.19
        p[cabin,0]+=.85
        lantern=p[:,0]>3.8
        p[lantern,1]+=.38
    if item['name']=='Flag':p[:,1]+=.62
    if item['group']=='Airship':
        factor=1.16 if item['name']=='Gondola' else 1.065
        p[:,0]=p[:,0]*factor+.3
    coords=np.c_[p[:,0],-p[:,2],p[:,1]]
    mesh=bpy.data.meshes.new(item['name']+'Mesh')
    mesh.from_pydata(coords.tolist(),[],np.arange(len(coords)).reshape(-1,3).tolist())
    mesh.update()
    obj=bpy.data.objects.new(item['name'],mesh);groups[item['group']].objects.link(obj);obj.parent=roots[item['group']]
    assign_colors(obj,colors=colors)
    # Weld duplicated triangle vertices without smoothing the low-poly normals.
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.001)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(mesh);bm.free();mesh.update()
    if item['name'] in ['Terrain','SnowRange','ForegroundCliffs','Water']:
        landscape_uv(mesh)
        mesh.materials.clear();mesh.materials.append(terrain_material)
    obj['source']='Blender reference control mesh; welded editable topology'
    print('MODELED',obj.name,len(mesh.vertices),'vertices',flush=True)

# Native Blender ico-sphere balloon: flat polygon faces and a tailored ellipsoid.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1)
balloon=bpy.context.object;balloon.name='Envelope'
balloon.scale=(6.55,3.17,4.20);balloon.location=(.3,0,5.0)
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
into_group(balloon,'Airship');assign_colors(balloon,base=color_hex('f5ecd8'),ambient=.70)
balloon['modeling']='Native Blender ico-sphere, shaped into a 13.1m ellipsoidal gas envelope'

def cable(name,points,radius,color,group='Airship'):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D'
    curve.resolution_u=1;curve.bevel_resolution=0;curve.bevel_depth=radius;curve.resolution_u=2
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,q in zip(spline.points,points):p.co=(*bl(q),1)
    obj=bpy.data.objects.new(name,curve);groups[group].objects.link(obj);obj.parent=roots[group]
    bpy.context.view_layer.objects.active=obj;obj.select_set(True)
    bpy.ops.object.convert(target='MESH');obj=bpy.context.object
    assign_colors(obj,base=color_hex(color));obj.select_set(False)
    return obj

def box(name,position,scale,color,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=bl(position))
    obj=bpy.context.object;obj.name=name;obj.scale=(scale[0],scale[2],scale[1])
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    if bevel:
        mod=obj.modifiers.new('Small hand-worked edges','BEVEL');mod.width=bevel;mod.segments=1
        bpy.ops.object.modifier_apply(modifier=mod.name)
    into_group(obj,'Airship');assign_colors(obj,base=color_hex(color));obj.select_set(False)
    return obj

# Belts follow the Blender balloon surface and have lighter edge stitching.
for index,x in enumerate([-5.75,.16,5.1]):
    radius=math.sqrt(max(.03,1-((x-.3)/6.55)**2))
    points=[[x,5.0+4.27*radius*math.cos(t),3.23*radius*math.sin(t)] for t in np.linspace(0,math.tau,80)]
    cable(f'Leather belt {index+1}',points,.067,'75664d')
    points=[[p[0]-.082,p[1],p[2]] for p in points]
    cable(f'Belt stitching {index+1}',points,.014,'c4b28f')

# Curved suspension ropes and deck railings are individual editable Blender objects.
for i,(ax,bx) in enumerate([(-4.7,-2.65),(4.25,2.78)]):
    for side in [-1,1]:
        anchor_y=5.0-4.2*math.sqrt(max(.01,1-((ax-.3)/6.55)**2-(1.86/3.17)**2))+.12
        a=np.array([ax,anchor_y,side*1.86]);b=np.array([bx,-1.55,side*1.18])
        points=[]
        for t in np.linspace(0,1,16):
            p=a*(1-t)+b*t;p[1]-=math.sin(t*math.pi)*.07;points.append(p)
        cable(f'Tension cable {i}_{side}',points,.038,'6c634a')
cable('Lantern suspension',[[5.114,2.50,.8],[5.114,.06,.8]],.024,'75664d')
for side in [-1,1]:
    points=[[x,-1.53+.15*math.cos(x),side*(1.15-.045*x*x)] for x in np.linspace(-2.8,2.9,40)]
    cable(f'Upper gunwale {side}',points,.072,'b1a079')
    for xa,xb in [(-2.75,-1.45),(-1.45,.1),(.1,1.5),(1.5,2.7)]:
        pts=[]
        for t in np.linspace(0,1,14):
            x=xa*(1-t)+xb*t;pts.append([x,-1.42-math.sin(t*math.pi)*.65,side*1.30])
        cable(f'Rope swag {side}_{xa}',pts,.032,'b7ab89')

# Cabin framing, chimney, louvered roof, and deck planks.
for x in [.0,.62,1.27]:
    box('Cabin upright '+str(x),[x,-.78,1.003],[.05,.85,.065],'c2aa7e',.012)
    box('Window crossbar '+str(x),[x,-.79,1.014],[.47,.055,.048],'ad946b',.008)
for y in [-.35,-1.21]:box('Cabin lintel '+str(y),[.65,y,1.01],[2.17,.08,.11],'aa946c',.013)
for z in np.linspace(-.97,.97,9):box('Roof board '+str(z),[.89,-.03,z],[2.6,.055,.14],'514c3d',.015)
for x in np.linspace(-2.35,-.7,7):box('Deck board '+str(x),[x,-1.66,.1],[.035,.028,1.75],'524a38')
box('Rear ballast chest',[2.55,-1.36,-.26],[.55,.43,.63],'78603f',.045)
box('Chest clasp',[2.55,-1.36,.075],[.09,.2,.035],'bbac82',.015)
cable('Boiler chimney',[[.451,-.04,-.13],[.451,.70,-.13]],.15,'4e4638')

# Fin and wooden spindle at the rear support the separately animated propeller.
cable('Rear propeller axle',[[5.6,3.6,0],[7.3,3.6,0]],.11,'786044')
cable('Flagstaff',[[.87,9.05,0],[.97,11.7,0]],.039,'6b6049')
for obj in groups['Airship'].objects:
    if obj.type=='MESH' and obj.name.startswith(('Cabin','Window','Roof board')):
        for v in obj.data.vertices:v.co.x+=.85

# Place the camera and the complete assembly for immediate inspection in Blender.
bpy.ops.mesh.primitive_plane_add(size=60000,location=(0,0,-.32))
ocean=bpy.context.object;ocean.name='OpenOcean';into_group(ocean,'Landscape')
assign_colors(ocean,base=color_hex('4588ae'))
ocean['purpose']='Continuous 3D ocean beyond the reference camera footprint'

ship_home=Vector(bl((-4.15,136.8,184)))
roots['Airship'].location=ship_home;roots['Airship'].rotation_euler.z=math.radians(13)
roots['Propeller'].location=ship_home+Matrix.Rotation(math.radians(13),4,'Z')@Vector(bl((7.3,3.6,0)))
roots['Propeller'].rotation_euler.z=math.radians(33)
roots['Propeller'].scale=(1.13,1.13,1.13)

bpy.ops.object.camera_add(location=bl((0,145,250)))
camera=bpy.context.object;camera.name='Reference Camera'
direction=Vector(bl((0,math.sin(math.radians(-3.5)),-math.cos(math.radians(-3.5)))))
camera.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
camera.data.type='PERSP';camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=24
camera.data.lens=12/math.tan(math.radians(25));camera.data.clip_end=25000
bpy.context.scene.camera=camera

bpy.ops.object.light_add(type='SUN',location=(0,-100,350))
sun=bpy.context.object;sun.name='Warm afternoon sun';sun.data.energy=2.1
sun.rotation_euler=(-SUN).to_track_quat('-Z','Y').to_euler();sun.data.angle=math.radians(4)
scene=bpy.context.scene;scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1672;scene.render.resolution_y=941;scene.render.resolution_percentage=100
scene.world.color=(.38,.56,.68)
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
scene['workflow']='Blender mesh authoring -> GLB -> Godot real-time 3D. No reference-image backdrop.'
scene['reference_view']='1672 x 941, 50 degree vertical FOV, pitch -3.5 degrees'

# Tailor the envelope axis and nose to the gentle pitch in the reference.
for obj in groups['Airship'].objects:
    if obj.type!='MESH':continue
    for v in obj.data.vertices:
        if v.co.z>1.0:
            v.co.z-=v.co.x*.043
            if v.co.x < -6.0:v.co.z+=.40

def export_group(name,filename):
    root=roots[name];old=root.matrix_world.copy();root.matrix_world=Matrix.Identity(4)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in groups[name].objects:obj.select_set(True)
    args=dict(filepath=str(ROOT/'assets'/filename),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_materials='EXPORT',export_cameras=False,export_lights=False)
    props=bpy.ops.export_scene.gltf.get_rna_type().properties
    if 'export_vertex_color' in props:
        options={e.identifier for e in props['export_vertex_color'].enum_items}
        if 'ACTIVE' in options:args['export_vertex_color']='ACTIVE'
    bpy.ops.export_scene.gltf(**args)
    root.matrix_world=old

export_group('Landscape','world.glb')
export_group('Airship','airship.glb')
export_group('Propeller','propeller.glb')
bpy.ops.object.select_all(action='DESELECT')
balloon.select_set(True);bpy.context.view_layer.objects.active=balloon
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA'
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.clip_end=25000
scene.render.filepath=str(ROOT/'captures/blender-model-preview.png')
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'blender/Aether.blend'))
print('BLENDER AUTHORING COMPLETE',bpy.app.version_string,'Objects:',len(bpy.data.objects),flush=True)
