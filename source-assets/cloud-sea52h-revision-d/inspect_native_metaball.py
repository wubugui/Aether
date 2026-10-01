import bpy,json
from pathlib import Path
P=Path(__file__).resolve().parent
bpy.ops.wm.read_factory_settings(use_empty=True)
mb=bpy.data.metaballs.new('Native density calibration');ob=bpy.data.objects.new('Native density calibration',mb);bpy.context.scene.collection.objects.link(ob)
e=mb.elements.new();e.type='ELLIPSOID';e.radius=100;e.size_x=2;e.size_y=1.5;e.size_z=1;e.stiffness=2
mb.resolution=8;mb.render_resolution=8;mb.threshold=.6
rows={p.identifier:{'type':p.type,'value':str(getattr(e,p.identifier,None))} for p in e.bl_rna.properties if p.identifier not in ['rna_type']}
bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');me=bpy.context.object.data
lo=[min(v.co[k] for v in me.vertices) for k in range(3)];hi=[max(v.co[k] for v in me.vertices) for k in range(3)]
r={'properties':rows,'threshold':.6,'radius':100,'size_xyz':[2,1.5,1],'native_mesh_dimensions':[b-a for a,b in zip(lo,hi)],'bounds':[lo,hi],'vertices':len(me.vertices)}
(P/'native-metaball-calibration.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
