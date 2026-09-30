import bpy,bmesh,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];folder=root/'captures/coastal_sky_assets_27a'
output=root/'reviews/round-27a-sky-native-check.json';assert not output.exists()
rows=[]
for asset in json.loads((folder/'model-report.json').read_text())['assets']:
    source=folder/(asset['asset']+'.blend');assert hashlib.sha256(source.read_bytes()).hexdigest()==asset['source_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source));parts=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        bm=bmesh.new();bm.from_mesh(obj.data);bm.transform(obj.matrix_world);bm.normal_update()
        volume=bm.calc_volume(signed=True)
        assert volume>0 and all(e.is_manifold for e in bm.edges) and all(f.calc_area()>1e-8 for f in bm.faces)
        parts.append({'name':obj.name,'volume_m3':volume,'vertices':len(bm.verts),'faces':len(bm.faces),'bounds':[[min(v.co[i] for v in bm.verts) for i in range(3)],[max(v.co[i] for v in bm.verts) for i in range(3)]]});bm.free()
    rows.append({'asset':asset['asset'],'source_sha256':asset['source_sha256'],'glb_sha256':asset['glb_sha256'],'parts':parts})
output.write_text(json.dumps({'passed':True,'scope':'Reopened saved Blender solids; actual mesh volume, edge closure and bounds. Does not prove visual fidelity.','assets':rows},indent=2))
print('SAVED SKY SOURCE CHECK PASSED',flush=True)
