import bpy,bmesh,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'captures/village_paving_study_24i/village_bay.blend'))
rows=[]
for obj in bpy.context.scene.objects:
    if not obj.name.startswith(('bay terrace bedding 8.550 3','bay worn stair paver 8.550 -3375 -2779')):continue
    bm=bmesh.new();bm.from_mesh(obj.data);bm.verts.ensure_lookup_table();bm.edges.ensure_lookup_table();bm.faces.ensure_lookup_table()
    edges=[{'vertices':[list(v.co) for v in e.verts],'indices':[v.index for v in e.verts],'faces':[[v.index for v in f.verts] for f in e.link_faces],'boundary':e.is_boundary,'wire':e.is_wire} for e in bm.edges if not e.is_manifold]
    rows.append({'name':obj.name,'verts':len(bm.verts),'faces':len(bm.faces),'bad_edges':edges});bm.free()
(root/'reviews/round-24i-native-defect-detail.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print(json.dumps(rows,indent=2),flush=True)
