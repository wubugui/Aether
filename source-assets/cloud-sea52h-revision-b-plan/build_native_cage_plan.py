"""Build only the three authored editing cages. No union, final asset, GLB or render."""
from pathlib import Path
import json,hashlib,bpy,bmesh
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
plan=json.loads((P/'cage52h_b.json').read_text())
protected=[ROOT/'source-assets/cloud-sea52h/cloud_sea52h_main.blend',ROOT/'source-assets/cloud-sea52h/cloud_sea_52h_main_v0.glb',ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p) for p in protected}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.threads_mode='FIXED';bpy.context.scene.render.threads=2
source=ROOT/'source-assets/cloud-sea52f/variants/cloud_sea52f_variants.blend'
with bpy.data.libraries.load(str(source),link=False) as (s,d):d.materials=[n for n in s.materials if n=='Cloud46 diffuse warm crown cool belly']
mat=d.materials[0]
col=bpy.data.collections.new('52h_B_CONTROL_CAGES_ONLY_NOT_FINAL');bpy.context.scene.collection.children.link(col)
for role,row in plan['parts'].items():
 me=bpy.data.meshes.new(role+'_authored_faces');me.from_pydata(row['vertices_blender_m'],[],row['oriented_triangles']);me.update()
 ob=bpy.data.objects.new('CAGE52hB_'+role,me);col.objects.link(ob);ob['role']=role;ob['state']='Unreviewed editing cage, not finished cloud';ob['coordinate_source']='cage52h_b.json';ob['positive_volume_only']=True;ob.show_wire=True;ob.show_all_edges=True
 me.materials.append(mat);colors=me.color_attributes.new('Col','FLOAT_COLOR','CORNER')
 for f in me.polygons:
  z=sum(me.vertices[i].co.z for i in f.vertices)/len(f.vertices);v=.76+.16*max(0,min(1,(z+190)/460));linear=((v+.055)/1.055)**2.4
  for li in f.loop_indices:colors.data[li].color=(linear,linear,linear,1)
 scene=bpy.context.scene
bpy.ops.wm.save_as_mainfile(filepath=str(P/'cage52h_b_plan.blend'))
bpy.ops.wm.open_mainfile(filepath=str(P/'cage52h_b_plan.blend'))
proof=[]
for role,row in plan['parts'].items():
 ob=bpy.data.objects['CAGE52hB_'+role];bm=bmesh.new();bm.from_mesh(ob.data)
 proof.append({'role':role,'vertices':len(bm.verts),'faces':len(bm.faces),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'signed_volume':bm.calc_volume(signed=True),'max_coordinate_error_m':max(abs(v.co[k]-row['vertices_blender_m'][i][k]) for i,v in enumerate(ob.data.vertices) for k in range(3))});bm.free()
assert all(r['boundary_edges']==0 and r['nonmanifold_edges']==0 and r['signed_volume']>0 and r['max_coordinate_error_m']<.0001 for r in proof)
after={str(p):sha(p) for p in protected};assert before==after
(P/'native-cage-readback.json').write_text(json.dumps({'cages':proof,'protected_before':before,'protected_after':after,'unchanged':True,'rendered':False,'union_built':False,'finished_cloud_built':False,'world_changed':False,'visual_acceptance':False},indent=2)+'\n')
print('THREE NATIVE EDITING CAGES REOPENED; NO FINAL SURFACE / RENDER / WORLD')
