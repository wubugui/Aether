"""Editable terrain-fitted harbor stone stairs and curved landings.
All geometry is local to each asset. Does not regenerate or overwrite the world.
"""
from pathlib import Path
import bpy,bmesh,math,json,shutil,hashlib
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'captures/village_paving_study_24g'
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
    bpy.context.scene['reference_images']='ref/1135.png;ref/1342.png'
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



source=ROOT/'captures/village_paving_design_24g/paving.json'
design=json.loads(source.read_text(encoding='utf-8'));shutil.copy2(source,OUT/'paving-design.json')
shutil.copy2(ROOT/'tools/prepare_village_paving_24g.py',OUT/'prepare-design.py')
materials=[mat('Village buried rubble masonry',(.095,.087,.066))]
for i,color in enumerate([(.150,.139,.112),(.162,.149,.121),(.141,.133,.110),(.173,.158,.129)]):materials.append(mat('Village worn limestone '+str(i),color))
for group in design['groups']:
    reset();origin=group['origin']
    for item in group['solids']:
        points=item['vertices_xz'];n=len(points)
        vertices=[(x-origin[0],-(z-origin[2]),y) for y in [item['bottom_y'],item['top_y']] for x,z in points]
        faces=[tuple(reversed(t)) for t in item['cap_triangles']]+[tuple(i+n for i in t) for t in item['cap_triangles']]
        faces.extend((a,b,b+n,a+n) for a,b in item['boundary_edges'])
        obj=mesh(item['name'],vertices,faces,materials[item['material']]);obj['world_top_y']=item['top_y'];obj['paving_role']=item['kind'];obj['world_origin']=origin
    freeze('village_'+group['name'],'Connected real stone courtyard and contour stairs for village '+group['name']+'. Actual headland-derived shared level field, separate thick limestone pavers and buried closed bedding. All door interfaces, ground envelope, widths and fidelity remain to verify in native World.')
(OUT/'model-report.json').write_text(json.dumps({'label':'24g','assets':reports,'source_headland_sha256':design['headland_glb_sha256'],'source_grid_run':design['source_grid_run'],'production_modified':False},indent=2),encoding='utf-8')
print('VILLAGE PAVING BUILT '+str(sum(a['parts'] for a in reports))+' EDITABLE SOLIDS',flush=True)
