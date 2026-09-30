from pathlib import Path
import bpy,bmesh,json,hashlib
from mathutils import Vector,Euler
R=Path(__file__).resolve().parents[1];P=R/'captures/lantern_island_study_31h'
out=P/'shoulder_authoring.blend';assert not out.exists()
e=json.loads((P/'geometry-evidence.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);destination=bpy.context.scene;destination.name='31h historical shoulder operands'
with bpy.data.libraries.load(str(P/'shoulder_operands.blend'),link=False) as (source,target):target.scenes=source.scenes
for imported in target.scenes:
    for o in list(imported.objects):destination.collection.objects.link(o)
    bpy.data.scenes.remove(imported)
objects=[o for o in destination.objects if o.type=='MESH'];assert len(objects)==len(e['additions'])
for o in objects:o.select_set(True)
bpy.context.view_layer.objects.active=objects[0]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_location=Vector((-5,-5,4))
            area.spaces.active.region_3d.view_distance=60
            area.spaces.active.region_3d.view_rotation=Euler((1.05,0,.6),'XYZ').to_quaternion()
bpy.ops.wm.save_as_mainfile(filepath=str(out));bpy.ops.wm.open_mainfile(filepath=str(out))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(objects)==len(e['additions'])
for spec in e['additions']:
    o=next(o for o in objects if o.name.startswith(spec['name']))
    sig=dict(vertices=[list(v.co) for v in o.data.vertices],polygons=[list(f.vertices) for f in o.data.polygons],materials=[f.material_index for f in o.data.polygons]);assert sig==spec['actual_operand_geometry']
    bm=bmesh.new();bm.from_mesh(o.data);assert all(x.is_manifold for x in bm.edges) and bm.calc_volume(signed=True)>0;bm.free()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(R/'reviews/round-31h-authoring-workspace-check.json').write_text(json.dumps(dict(passed=True,authoring_file=str(out.relative_to(R)),authoring_sha256=sha(out),library_sha256=sha(P/'shoulder_operands.blend'),mesh_objects_reopened_in_normal_startup_scene=len(objects),actual_operand_geometry_unchanged=True,scope='Normal Blender workspace saved and reopened, with three selected historical editable operands; final island has separate actual rear retopology. No GPU art acceptance or manual UI inspection claimed.'),indent=2))
print('31h NORMAL AUTHORING WORKSPACE REOPENED',flush=True)
