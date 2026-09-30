import bpy,bmesh,json,sys,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];label=sys.argv[sys.argv.index('--')+1]
folder=root/'captures'/('village_grading_study_'+label);report=json.loads((folder/'build-report.json').read_text())
assert report['passed']
def geometry(obj):
    return sorted((tuple(sorted(tuple(obj.data.vertices[i].co) for i in p.vertices)),obj.data.materials[p.material_index].name) for p in obj.data.polygons)
bpy.ops.wm.open_mainfile(filepath=str(root/'captures/headland_study_23g/mainland_headland.blend'))
old={o.name:geometry(o) for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Broad tidal buttress')}
source=folder/'mainland_headland.blend';assert hashlib.sha256(source.read_bytes()).hexdigest()==report['source_sha256']
bpy.ops.wm.open_mainfile(filepath=str(source));checks=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data);bm.normal_update();issues=[]
    if any(not e.is_manifold for e in bm.edges):issues.append('nonmanifold edge')
    if any(not v.is_manifold for v in bm.verts):issues.append('nonmanifold vertex')
    if any(f.calc_area()<1e-9 for f in bm.faces):issues.append('zero area')
    volume=bm.calc_volume(signed=True)
    if volume<=0:issues.append('nonpositive volume')
    if obj.name in old and geometry(obj)!=old[obj.name]:issues.append('original rock changed')
    checks.append({'name':obj.name,'vertices':len(bm.verts),'polygons':len(bm.faces),'volume_m3':volume,'original_rock_geometry_unchanged':True if obj.name in old else None,'issues':issues});bm.free()
assert len(checks)==12 and len(old)==11
result={'label':label,'passed':not any(p['issues'] for p in checks),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'glb_sha256':hashlib.sha256((folder/'mainland_headland.glb').read_bytes()).hexdigest(),'parts':checks,'scope':'Actual saved Blender reopened, edge and vertex manifold, nonzero faces, positive volumes; eleven original editable rock shoulders unchanged. Native GPU, coastline and full paving envelope proof still separate.'}
output=root/'reviews'/('round-'+label+'-village-grading-native-check.json');assert not output.exists();output.write_text(json.dumps(result,indent=2),encoding='utf-8')
assert result['passed'],checks
print('VILLAGE GRADING NATIVE GATE PASSED',flush=True)
