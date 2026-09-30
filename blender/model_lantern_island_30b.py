"""Authored coastal facets: replace circumferential bands with local fracture panels."""
from pathlib import Path
import bpy,bmesh,json,math,hashlib,shutil
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
SRC=R/'captures/lantern_island_study_30a/island_c.blend'
OUT=R/'captures/lantern_island_study_30b'
assert not OUT.exists();OUT.mkdir()
shutil.copy2(__file__,OUT/'builder.py')
plan=json.loads((SRC.parent/'proportion-plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(SRC))
tn='island_c grass and exposed rock terrain';pn='island_c terrain fitted keeper paths';cn='island_c faulted bedrock'
def sig(o):return dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(p.vertices) for p in o.data.polygons],materials=[p.material_index for p in o.data.polygons])
old={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
terrain=bpy.data.objects[tn];core=bpy.data.objects[cn]
n=plan['top_vertex_count'];mapping=plan['core_boundary_map']
lower=[Vector(v.co) for v in terrain.data.vertices[n:]]
cap=[lower[j] for j in mapping]
oldwater=[Vector(v) for v in old[cn]['vertices'][18:36]]
# Coast changes are authored by boundary sector. These are irregular breaks,
# not random height noise or additional circumferential terrace rings.
water_z=[-.35,.42,-.22,.65,.08,-.30,.48,-.18,.20,-.40,.52,-.16,.35,-.32,.08,.55,-.18,.28]
reach=[1.03,1.00,1.07,1.02,1.08,1.01,1.00,1.05,1.03,1.01,1.04,1.00,1.01,1.00,1.00,1.04,1.03,1.00]
water=[Vector((v.x*reach[i],v.y*reach[i],water_z[i])) for i,v in enumerate(oldwater)]
bottom=[Vector((v.x,v.y,-5.85)) for v in water]
centers=[]
fractions=[.28,.67,.35,.52,.72,.31,.60,.40,.74,.34,.58,.26,.64,.46,.30,.70,.38,.61]
for i in range(18):
    j=(i+1)%18
    # A point inside the projected quadrilateral; height creates a short,
    # local fracture shoulder. No edge connects adjacent sector centers.
    q=(water[i]+water[j]+cap[i]+cap[j])*.25
    q.z=(water[i].z+water[j].z)*.5*(1-fractions[i])+(cap[i].z+cap[j].z)*.5*fractions[i]
    centers.append(q)
verts=bottom+water+centers+lower
faces=[list(reversed(range(18)))]
for i in range(18):
    j=(i+1)%18
    faces.extend([[i,j,18+j],[i,18+j,18+i]])
    loop=[18+i,18+j,54+mapping[j],54+mapping[i]]
    for a,b in zip(loop,loop[1:]+loop[:1]):faces.append([a,b,36+i])
for p in terrain.data.polygons:
    if all(i<n for i in p.vertices):faces.append([54+i for i in p.vertices])
mats=list(core.data.materials);mesh=bpy.data.meshes.new('30b local fractured coast');mesh.from_pydata(verts,[],faces);mesh.update();core.data=mesh
for mat in mats:mesh.materials.append(mat)
for p in mesh.polygons:p.material_index=2 if p.center.z<-.7 else (1 if p.normal.x<-.55 else 0)
shoulders=[
 ('West broken shoulder',(1.0,.2),.63),
 ('Southwest leaning crag',(.4,1.0),.70),
 ('South broad low spur',(-.3,1.1),.57),
 ('East high fracture',(-1.5,.4),.61),
 ('Northeast sloping shoulder',(-.8,-.9),.69),
 ('North broken ridge',(.2,-1.0),.62),
 ('Northwest split buttress',(.7,-.3),.66)]
edits=[]
for name,shift,height in shoulders:
    o=bpy.data.objects[name];vs=o.data.vertices;center=sum((v.co for v in vs),Vector())/len(vs)
    outward=Vector((center.x,center.y));outward.normalize()
    for v in vs:
        xy=Vector((v.co.x-center.x,v.co.y-center.y))
        # Short, broad shoulder; the outer face slopes toward its tidal root.
        v.co.x=center.x+xy.x*1.08+shift[0];v.co.y=center.y+xy.y*1.08+shift[1]
        if v.co.z>0:v.co.z=max(.35,v.co.z*height-.10*xy.dot(outward))
    edits.append(dict(name=name,shift_xy=shift,width_factor=1.08,positive_height_factor=height,outward_slope=.10))
roots=[('West rooted toe','West broken shoulder',.28),('Southwest wash ledge','Southwest leaning crag',.26),('South low reef','South broad low spur',.34),('East submerged root','East high fracture',.32),('Northeast low cluster','Northeast sloping shoulder',.28),('North tidal end','North broken ridge',.32),('Northwest rooted slab','Northwest split buttress',.30),('West waterline satellite','West rooted toe',.42),('South low satellite','South low reef',.46),('East tidal satellite','East submerged root',.42)]
for name,parent,amount in roots:
    o=bpy.data.objects[name];target=bpy.data.objects[parent]
    center=sum((v.co for v in o.data.vertices),Vector())/len(o.data.vertices)
    to=sum((v.co for v in target.data.vertices),Vector())/len(target.data.vertices)
    shift=(to-center)*amount;shift.z=0
    for v in o.data.vertices:v.co+=shift
    edits.append(dict(name=name,root_toward=parent,fraction=amount,shift=list(shift)))
native=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    if o.name not in [tn,pn]:
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    bm=bmesh.new();bm.from_mesh(o.data)
    assert all(e.is_manifold for e in bm.edges),o.name
    assert all(f.calc_area()>1e-10 for f in bm.faces),o.name
    volume=bm.calc_volume(signed=True);assert volume>0,(o.name,volume)
    bm.free();native.append(dict(name=o.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),volume_m3=volume))
assert sig(terrain)==old[tn] and sig(bpy.data.objects[pn])==old[pn]
plan.update(scope='30b replace core middle ring with disconnected local fracture-panel centers, irregular lower coastline, shortened broad shoulders and clustered tidal roots. 30a terrain/path/pads exactly retained; native buildings and same-world D placement unchanged.',core_cap_offset=54,core_side_topology='18 independent panel centers, no middle-ring edges',shoreline_water_z=water_z,shoreline_reach=reach,fracture_height_fractions=fractions,rock_edits=edits)
(OUT/'proportion-plan.json').write_text(json.dumps(plan,indent=2))
bpy.context.scene['scope']=plan['scope'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
new={o.name:sig(o) for o in bpy.context.scene.objects if o.type=='MESH'}
(OUT/'geometry-evidence.json').write_text(json.dumps(dict(old=old,new=new,sites=plan['sites'],land_scale=[1,1,1],changes=edits)),encoding='utf-8')
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
(OUT/'model-report.json').write_text(json.dumps(dict(label='30b',source_basis=str(SRC.relative_to(R)),source_basis_sha256=sha(SRC),source_sha256=sha(OUT/'island_c.blend'),glb_sha256=sha(OUT/'island_c.glb'),native=native,scope=plan['scope']),indent=2))
print('30b NATIVE COAST SAVED',flush=True)
