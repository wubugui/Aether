"""Editable real spatial weather primitives, without images or camera input."""
import bpy, bmesh, math, random, os, json
from pathlib import Path
from mathutils import Vector
out=Path(os.environ['HUB_OUTPUT_DIR']);out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
def material(name,color):
    mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);return mat
rainmat=material('Rain pale blue',(.46,.60,.76))
snowmat=material('Snow white',(.90,.94,1))
boltmat=material('Lightning core',(.94,.79,1))
report={'scope':'Independent editable rain streak, snow crystal, branching lightning, seven-band physical rainbow. Engine controls emission, particle movement, timing and local illumination.','assets':[]}
def collection(name):
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col);return col
def cylinder(col,name,a,b,r,mat):
    direction=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
    bm=bmesh.new();bmesh.ops.create_cone(bm,cap_ends=True,cap_tris=True,segments=5,radius1=r,radius2=r*.7,depth=direction.length)
    rotation=direction.to_track_quat('Z','Y').to_matrix()
    for v in bm.verts:v.co=rotation@v.co+mid
    mesh=bpy.data.meshes.new(name);bm.to_mesh(mesh);bm.free();mesh.materials.append(mat)
    obj=bpy.data.objects.new(name,mesh);col.objects.link(obj)
def export(col,name):
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.all_objects:obj.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(out/(name+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    report['assets'].append({'name':name,'editable_mesh_parts':len(col.objects)})
col=collection('rain_streak42b');cylinder(col,'rain_streak',(0,0,-1.6),(0,0,1.6),.022,rainmat);export(col,col.name)
col=collection('snow_crystal42b');bm=bmesh.new();bmesh.ops.create_icosphere(bm,subdivisions=1,radius=.12)
mesh=bpy.data.meshes.new('snow_crystal');bm.to_mesh(mesh);bm.free();mesh.materials.append(snowmat)
obj=bpy.data.objects.new('snow_crystal',mesh);col.objects.link(obj);export(col,col.name)
for variant in range(3):
    col=collection('lightning42b_'+str(variant));rng=random.Random(4200+variant*11)
    points=[Vector((0,0,0))]
    for i in range(1,18):points.append(Vector((rng.uniform(-25,25),rng.uniform(-12,12),-i*24)))
    for i in range(17):cylinder(col,'trunk_%02d'%i,points[i],points[i+1],1.2-i*.035,boltmat)
    for branch in [4,8,11]:
        a=points[branch];sign=-1 if branch==8 else 1
        for j in range(4):
            b=a+Vector((sign*rng.uniform(15,35),rng.uniform(-12,12),-rng.uniform(15,38)))
            cylinder(col,f'branch_{branch}_{j}',a,b,.55-j*.08,boltmat);a=b
    export(col,col.name)
col=collection('rainbow42b')
colors=[(1,.2,.2),(1,.5,.13),(1,.87,.25),(.26,.9,.48),(.2,.62,1),(.44,.36,1),(.7,.34,.9)]
for band,color in enumerate(colors):
    verts=[];faces=[];r=900-band*8
    for i in range(97):
        angle=math.pi*i/96
        for radius in [r-8,r]:verts.append((radius*math.cos(angle),0,radius*math.sin(angle)))
    for i in range(96):faces.append((i*2,i*2+1,i*2+3,i*2+2))
    mesh=bpy.data.meshes.new('spectrum_band_'+str(band));mesh.from_pydata(verts,[],faces);mesh.materials.append(material('Rainbow spectrum '+str(band),color))
    obj=bpy.data.objects.new('spectrum_band_'+str(band),mesh);col.objects.link(obj)
export(col,col.name)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'weather42b.blend'))
(out/'weather42b-model-report.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('WEATHER42B MODELED',json.dumps(report))
