"""Resculpt saved C/D terrain and interlocking low fractured shoulders."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
from mathutils import Vector
R=Path(__file__).resolve().parents[1];SRC=R/'captures/lantern_island_study_29a/island_c.blend';OUT=R/'captures/lantern_island_study_29b'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((R/'captures/island-29b-terrain-plan.json').read_text());shutil.copy2(R/'captures/island-29b-terrain-plan.json',OUT/'terrain-plan.json')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
terrain=bpy.data.objects['island_c grass and exposed rock terrain'];path=bpy.data.objects['island_c terrain fitted keeper paths'];core=bpy.data.objects['island_c faulted bedrock']
def sig(o):return {'vertices':[list(v.co) for v in o.data.vertices],'polygons':[list(p.vertices) for p in o.data.polygons],'materials':[p.material_index for p in o.data.polygons]}
old={role:sig(o) for role,o in [('terrain',terrain),('path',path),('core',core)]}
n=plan['top_vertex_count']
assert len(core.data.vertices)==72+n
for i,co in enumerate(plan['terrain_vertices']):terrain.data.vertices[i].co=co
for i in range(n):
    assert max(abs(old['core']['vertices'][72+i][k]-old['terrain']['vertices'][n+i][k]) for k in range(3))<2e-6
    core.data.vertices[72+i].co=terrain.data.vertices[n+i].co
for i in range(18):
    coast=core.data.vertices[18+i].co
    j=min(range(n),key=lambda j:(old['terrain']['vertices'][j][0]-coast.x*.9)**2+(old['terrain']['vertices'][j][1]-coast.y*.9)**2)
    ratio=max(1.5,terrain.data.vertices[n+j].co.z)/max(1.5,old['terrain']['vertices'][n+j][2])
    for level in [2,3]:core.data.vertices[level*18+i].co.z*=ratio
terrain.data.update();core.data.update()
protected=set(plan['protected_face_indices'])
for p in terrain.data.polygons:
    if max(p.vertices)<n and p.index not in protected:
        p.material_index=2 if p.normal.z<.90 or p.center.z<8.4 else 0
    elif min(p.vertices)>=n:p.material_index=1

primary=[('West broken shoulder',(-29,-13),20,14,1.12,.93),('Southwest leaning crag',(-27,-32),14,9.5,1.22,.85),('South broad low spur',(-1,-31),12,8,1.35,.78),('East high fracture',(31,-18),21,12.5,1.20,.93),('Northeast sloping shoulder',(27,21),18,11.5,1.08,1.05),('North broken ridge',(-2,31),16,10,1.25,.8),('Northwest split buttress',(-24,16),19,13.5,1.1,.95)]
changes=[]
for idx,(name,(cx,cy),h,nh,sx,sy) in enumerate(primary):
    o=bpy.data.objects[name];toward=Vector((-cx,-cy)).normalized()*2.0
    before=sig(o)
    for v in o.data.vertices:
        x,y,z=v.co;v.co.x=cx+(x-cx)*sx+toward.x;v.co.y=cy+(y-cy)*sy+toward.y
        if z>-.7:
            v.co.z=-.7+(z+.7)*nh/h
            # Broad upper ridge leans inward, rather than narrowing into a post.
            v.co.x+=toward.x*.40*(z+.7)/h;v.co.y+=toward.y*.40*(z+.7)/h
    changes.append({'name':name,'before':before,'after':sig(o),'height_scale':nh/h})

# Leave unequal water gaps; merge the visual rhythm into three broad reef groups.
remove=['West fracture foot','Southwest dark toe','South inset boulder','East small ledge','Northeast washstone','North broken toe','Northwest outer crag']
for name in remove:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
reef=[('West rooted toe',(-39,-19),1.5,.72,.52),('Southwest wash ledge',(-25,-41),1.28,.85,.58),('South low reef',(9,-37),1.42,.68,.60),('East submerged root',(38,-21),.85,1.35,.56),('Northeast low cluster',(36,24),1.4,.72,.48),('North tidal end',(-2,42),1.55,.65,.70),('Northwest rooted slab',(-35,19),1.30,.78,.56),('West waterline satellite',(-45,-22),1.5,.65,.6),('South low satellite',(13,-41),1.8,.75,.65),('East tidal satellite',(44,-14),1.6,.7,.5)]
for name,(cx,cy),sx,sy,sz in reef:
    o=bpy.data.objects[name];before=sig(o)
    for v in o.data.vertices:
        v.co.x=cx+(v.co.x-cx)*sx;v.co.y=cy+(v.co.y-cy)*sy
        if v.co.z>-.7:v.co.z=-.7+(v.co.z+.7)*sz
    changes.append({'name':name,'before':before,'after':sig(o),'height_scale':sz})

native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),o.name
    assert all(f.calc_area()>1e-9 for f in bm.faces),o.name
    volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
    bm.to_mesh(o.data);bm.free();o.data.update()
    native.append({'name':o.name,'vertices':len(o.data.vertices),'faces':len(o.data.polygons),'volume_m3':volume})
assert sig(path)==old['path']
for i in plan['protected_vertex_indices']:assert list(terrain.data.vertices[i].co)==old['terrain']['vertices'][i]
for i in plan['protected_face_indices']:assert terrain.data.polygons[i].material_index==old['terrain']['materials'][i]
bpy.context.scene['scope']='29b true peripheral terrain remodeling; protected road/pad/tree triangles retained. Low/wide embedded shoulders and fewer flattened tidal groups. Visual review pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
evidence={'old':old,'new':{o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'},'protection':plan['protection'],'protected_face_indices':plan['protected_face_indices'],'protected_vertex_indices':plan['protected_vertex_indices'],'removed_parts':remove,'rock_changes':changes}
(OUT/'geometry-evidence.json').write_text(json.dumps(evidence),encoding='utf-8')
groups={}
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
for material,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    bpy.context.object.name='island_c_'+material
bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.gltf(filepath=str(OUT/'island_c.glb'),export_format='GLB',use_selection=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'model-report.json').write_text(json.dumps({'label':'29b','source_basis':str(SRC.relative_to(R)),'source_basis_sha256':sha(SRC),'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'native':native,'changed_top_vertices':plan['changed_top_vertices'],'protected_faces':len(protected),'scope':bpy.context.scene['scope']},indent=2))
print('29b SAVED AND EXPORTED '+str(len(native)),flush=True)
