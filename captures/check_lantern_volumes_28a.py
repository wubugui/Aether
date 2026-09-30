import bpy,bmesh,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];folder=R/'captures/lantern_volume_assets_28a';out=R/'reviews/round-28a-lantern-native-check.json'
assert not out.exists();rows=[]
for record in json.loads((folder/'model-report.json').read_text())['assets']:
    p=folder/(record['asset']+'.blend');assert hashlib.sha256(p.read_bytes()).hexdigest()==record['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(p));parts=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bm.normal_update()
        assert all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-9 for f in bm.faces) and bm.calc_volume(signed=True)>0
        parts.append({'name':obj.name,'bounds':[[min(v.co[i] for v in bm.verts) for i in range(3)],[max(v.co[i] for v in bm.verts) for i in range(3)]],'volume_m3':bm.calc_volume(signed=True)});bm.free()
    rows.append({'asset':record['asset'],'source_sha256':record['source_sha256'],'glb_sha256':record['glb_sha256'],'parts':parts})
out.write_text(json.dumps({'passed':True,'scope':'Reopened actual saved Blender solids; volume/closure/bounds. Runtime light and visual fidelity remain unproven.','assets':rows},indent=2))
print('LANTERN VOLUMES SAVED SOURCE PASSED',flush=True)
