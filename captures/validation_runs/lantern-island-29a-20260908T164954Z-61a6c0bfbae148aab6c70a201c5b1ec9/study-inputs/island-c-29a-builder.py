"""Refine saved C/D island rock mass; retain actual terrain and path geometry."""
from pathlib import Path
import bpy,bmesh,math,json,hashlib,shutil
from mathutils import Vector
from mathutils.geometry import convex_hull_2d,intersect_line_line_2d
R=Path(__file__).resolve().parents[1]
SRC=R/'captures/lantern_islands_study_20l/island_c.blend'
OUT=R/'captures/lantern_island_study_29a'
assert not OUT.exists();OUT.mkdir();shutil.copy2(__file__,OUT/'builder.py')
bpy.ops.wm.open_mainfile(filepath=str(SRC))
terrain=bpy.data.objects['island_c grass and exposed rock terrain']
path=bpy.data.objects['island_c terrain fitted keeper paths']
core=bpy.data.objects['island_c faulted bedrock']
def signature(obj):
    return {'vertices':[list(v.co) for v in obj.data.vertices], 'polygons':[list(p.vertices) for p in obj.data.polygons], 'materials':[p.material_index for p in obj.data.polygons]}
original={'terrain':signature(terrain),'path':signature(path),'core':signature(core)}
rock=next(m for m in core.data.materials if m.name.startswith('Coast blue grey'))
face=next(m for m in core.data.materials if m.name.startswith('Coast exposed'))
dark=next(m for m in core.data.materials if m.name.startswith('Coast tidal'))
road_polys=[[Vector((path.data.vertices[i].co.x,path.data.vertices[i].co.y)) for i in p.vertices] for p in path.data.polygons if p.normal.z>.5]
assert len(road_polys)==259,len(road_polys)
def rect(cx,cy,wx,wy,turn):
    co,si=math.cos(turn),math.sin(turn)
    return [Vector((cx+co*x-si*y,cy+si*x+co*y)) for x,y in [(-wx,-wy),(wx,-wy),(wx,wy),(-wx,wy)]]
pads=[rect(1,1,5.4,5.4,.1),rect(-12,-14,4.4,6.5,-.15)]
trees=[(-17.5,4.5),(-20,2),(-17,-1),(-15.5,-7),(-13,-10),(8,10.5),(11.5,9),(15,7),(19.5,-2.5),(21,-5.5),(9,-11)]
def inside(p,poly):
    yes=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a.y>p.y)!=(b.y>p.y) and p.x<(b.x-a.x)*(p.y-a.y)/(b.y-a.y)+a.x:yes=not yes
    return yes
def point_edge(p,a,b):
    edge=b-a;t=max(0.,min(1.,(p-a).dot(edge)/max(edge.length_squared,1e-12)))
    return (p-a-edge*t).length
def gap(a,b):
    if inside(a[0],b) or inside(b[0],a):return 0.
    result=1e10
    for u,v in zip(a,a[1:]+a[:1]):
        for x,y in zip(b,b[1:]+b[:1]):
            if intersect_line_line_2d(u,v,x,y) is not None:return 0.
            result=min(result,point_edge(u,x,y),point_edge(v,x,y),point_edge(x,u,v),point_edge(y,u,v))
    return result
removed=[]
for obj in list(bpy.context.scene.objects):
    if 'cliff outcrop' in obj.name or 'low shore ledge' in obj.name:
        removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)

# Saved bedrock has18 boundary controls per ring, followed by the exact terrain
# underside. Keep water-bottom and top support topology; stagger the fractures.
count=18
assert all(abs(core.data.vertices[i].co.z+9)<1e-5 for i in range(count))
lower_fraction=[.19,.51,.26,.60,.33,.46,.20,.55,.28,.59,.31,.16,.50,.24,.57,.36,.18,.46]
upper_fraction=[.86,.78,.91,.83,.88,.93,.75,.86,.81,.91,.77,.87,.92,.79,.88,.82,.90,.78]
ring_changes=[]
for i in range(count):
    coast=core.data.vertices[count+i].co.copy();x,y=coast.x,coast.y
    # Exact top rim recovered from old vertex correspondence by XY proximity.
    target=min(core.data.vertices[4*count:],key=lambda v:(v.co.x-x*.9)**2+(v.co.y-y*.9)**2).co.copy()
    old2=core.data.vertices[2*count+i].co.copy();old3=core.data.vertices[3*count+i].co.copy()
    h=max(target.z,3.)
    before=core.data.vertices[count+(i-1)%count].co;after=core.data.vertices[count+(i+1)%count].co
    tangent=Vector((after.x-before.x,after.y-before.y));outward=Vector((tangent.y,-tangent.x)).normalized()
    for level,frac in [(2,lower_fraction[i]),(3,upper_fraction[i])]:
        v=core.data.vertices[level*count+i]
        # More inclined recesses alternate with broad standing fracture cheeks.
        blend=(.42 if level==2 else .82)
        shift=([-.8,1.5,-1.6,.3,-.4,1.0,.4,-1.1,.8][i%9] if level==2 else [.2,-1.1,.7,-.4,.9,-.8][i%6])
        p=Vector((x,y)).lerp(Vector((target.x,target.y)),blend)+outward*shift
        v.co=(p.x,p.y,max(1.2,h*frac))
    ring_changes.append({'index':i,'old_mid':list(old2),'new_mid':list(core.data.vertices[2*count+i].co),'old_upper':list(old3),'new_upper':list(core.data.vertices[3*count+i].co)})
core.data.update()

# Authored, unequal fracture shoulders grouped into seven dominant masses;
# not an evenly spaced ring, random scatter or a second grass cone.
design=[
('West broken shoulder',(-29,-13),(8,9),20,-.12),
('Southwest leaning crag',(-27,-32),(9,7),14,.20),
('South broad low spur',(-1,-31),(10,7),12,-.15),
('East high fracture',(31,-18),(7,9),21,.13),
('Northeast sloping shoulder',(27,21),(8,10),18,-.23),
('North broken ridge',(-2,31),(11,8),16,.12),
('Northwest split buttress',(-24,16),(10,9),19,-.15),
('West rooted toe',(-39,-19),(5,6),8,-.30),
('West fracture foot',(-35,-27),(5,7),7,.15),
('Southwest wash ledge',(-25,-41),(7,5),5,.13),
('Southwest dark toe',(-35,-37),(5,4),6,-.26),
('South low reef',(9,-37),(6,4),5,.25),
('South inset boulder',(-10,-40),(5,5),4,-.18),
('East submerged root',(38,-21),(4,7),6,.10),
('East small ledge',(39,-10),(4,5),4,-.16),
('Northeast low cluster',(36,24),(5,7),5,.31),
('Northeast washstone',(28,34),(6,4),5,-.20),
('North tidal end',(-2,42),(6,4),4,.13),
('North broken toe',(-12,38),(5,4),6,-.31),
('Northwest rooted slab',(-35,19),(6,5),7,.11),
('Northwest outer crag',(-32,30),(5,4),6,-.23),
('West waterline satellite',(-45,-22),(3,3.5),3,-.10),
('South low satellite',(13,-41),(3,2.2),2.2,.25),
('East tidal satellite',(44,-14),(2.5,3.5),2.5,-.20)]
base=[(-1,-.55),(-.62,-.95),(.50,-.85),(1,-.25),(.85,.50),(.15,1),(-.68,.76),(-.98,.05)]
upper=[(-.70,-.48,.57),(-.20,-.73,.80),(.58,-.43,.95),(.75,.12,.89),(.14,.53,1.03),(-.61,.35,.72)]
added=[]
for idx,(name,center,size,height,turn) in enumerate(design):
    cx,cy=center;sx,sy=size;co,si=math.cos(turn),math.sin(turn)
    points=[]
    for x,y in base:points.append(Vector((cx+co*x*sx-si*y*sy,cy+si*x*sx+co*y*sy,-3.5 if height<9 else -5.)))
    # Each broad face belongs to a shared inclined fracture direction.
    for x,y,z in upper:
        x+=.12*math.sin(idx*.8);y+=.08*math.cos(idx*.6)
        points.append(Vector((cx+co*x*sx-si*y*sy,cy+si*x*sx+co*y*sy,-.7+height*z)))
    hull2=[Vector((p.x,p.y)) for p in points];outline=[hull2[i] for i in convex_hull_2d(hull2)]
    road_gap=min(gap(outline,p) for p in road_polys);pad_gap=min(gap(outline,p) for p in pads)
    tree_gap=min(0. if inside(Vector(p),outline) else min(point_edge(Vector(p),a,b) for a,b in zip(outline,outline[1:]+outline[:1])) for p in trees)
    assert road_gap>=1.2,(name,'road',road_gap)
    assert pad_gap>=.2,(name,'pad',pad_gap)
    assert tree_gap>=1.5,(name,'tree',tree_gap)
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    result=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    interior=[v for v in result.get('geom_interior',[]) if isinstance(v,bmesh.types.BMVert)]
    if interior:bmesh.ops.delete(bm,geom=interior,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    data=bpy.data.meshes.new(name+' authored fracture');bm.to_mesh(data);bm.free()
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj)
    for m in [rock,face,dark]:data.materials.append(m)
    for p in data.polygons:
        p.material_index=2 if p.center.z<1 else (1 if p.normal.x<-.30 and p.normal.z<.75 else 0)
    obj['authoring_role']='Independent closed fractured rock shoulder' if idx<7 else 'Independent rooted/tidal reef fragment'
    added.append({'name':name,'road_projection_clearance_m':road_gap,'padded_foundation_clearance_m':pad_gap,'tree_axis_projection_clearance_m':tree_gap,'vertices':len(data.vertices),'faces':len(data.polygons)})

assert signature(terrain)==original['terrain'];assert signature(path)==original['path']
assert signature(core)['vertices'][4*count:]==original['core']['vertices'][4*count:]
native=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges),(obj.name,'not closed')
    assert all(f.calc_area()>1e-9 for f in bm.faces),(obj.name,'zero face')
    vol=bm.calc_volume(signed=True);assert vol>0,(obj.name,vol)
    bm.to_mesh(obj.data);bm.free();native.append({'name':obj.name,'vertices':len(obj.data.vertices),'faces':len(obj.data.polygons),'volume_m3':vol})
assert signature(terrain)==original['terrain'];assert signature(path)==original['path']
bpy.context.scene['scope']='29a editable C/D geological remodeling; actual20l terrain/path/source interfaces retained. Visual and scene validation pending.'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'island_c.blend'))
dump={'old':original,'new':{o.name:signature(o) for o in bpy.context.scene.objects if o.type=='MESH'},'protection':{'path_top_triangles':[[list(v) for v in p] for p in road_polys],'pads':[[list(v) for v in p] for p in pads],'trees':trees}}
(OUT/'geometry-evidence.json').write_text(json.dumps(dump),encoding='utf-8')
# Keep all authored parts in the saved BLEND; batch only an export copy.
groups={}
for o in list(bpy.context.scene.objects):
    if o.type=='MESH':groups.setdefault(o.data.materials[0].name,[]).append(o)
for material,objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    bpy.context.object.name='island_c_'+material
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.gltf(filepath=str(OUT/'island_c.glb'),export_format='GLB',use_selection=True,export_apply=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report={'label':'29a','source_basis':str(SRC.relative_to(R)),'source_basis_sha256':sha(SRC),'source_sha256':sha(OUT/'island_c.blend'),'glb_sha256':sha(OUT/'island_c.glb'),'native_closed_solids_passed':True,'unchanged_terrain_and_paths':True,'unchanged_core_top_support_vertices':True,'removed_old_parts':removed,'new_parts':added,'native':native,'core_ring_edits':ring_changes,'scope':'C/D only; designed fracture masses in original geological palette. Independent closed volumes intentionally interlock/bed into shared core; not a boolean-union/intersection-free claim. Runtime placement/collision and visual acceptance pending.'}
(OUT/'model-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('29a C/D FRACTURED ROCK BUILT '+json.dumps({'parts':len(native),'new_crags':len(added)}),flush=True)
