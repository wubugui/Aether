import bpy, json, collections, os
from mathutils import Vector
from mathutils.kdtree import KDTree
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake-rim53'
ROOT='/workspace/scratch/a29d03198654/Aether'
a=json.load(open(D+'/base51b-headless.json'))
paths={'massif_west_spur':D+'/original_west_spur.blend','massif_cirque_wall':ROOT+'/source-assets/lake48/massif_cirque_wall_lake48.blend','massif_east_foothill':ROOT+'/source-assets/lake48/massif_east_foothill_lake48.blend','massif_frost_crown':ROOT+'/cloud-evidence/lake-source-intake/massif_frost_crown.blend'}
report=[]
for n,p in paths.items():
 bpy.ops.wm.open_mainfile(filepath=p)
 o=next(o for o in bpy.data.objects if o.type=='MESH');m=o.data;m.calc_loop_triangles();r=a['meshes'][n];org=Vector(r['origin'])
 kd=KDTree(len(r['faces']))
 for i,p in enumerate(r['faces']):kd.insert(p,i)
 kd.balance();mapped=[];dist=[]
 for v in m.vertices:
  p=o.matrix_world@v.co;q=Vector((p.x+org.x,p.z+org.y,-p.y+org.z));near,idx,d=kd.find(q);mapped.append(near);dist.append(d)
 def key(t):return tuple(sorted(tuple(round(x,4) for x in p) for p in t))
 before=collections.Counter(key(r['faces'][i:i+3]) for i in range(0,len(r['faces']),3));after=collections.Counter(key([mapped[i] for i in t.vertices]) for t in m.loop_triangles)
 info={'name':n,'path':paths[n],'objects':[{'name':x.name,'type':x.type} for x in bpy.data.objects],'vertices':len(m.vertices),'triangles':len(m.loop_triangles),'saved_triangles':len(r['faces'])//3,'source_to_saved_max_distance':max(dist),'exact_topology_after_nearest_mapping':before==after,'matrix_world':[list(row) for row in o.matrix_world],'color_attributes':[{'name':x.name,'domain':x.domain,'type':x.data_type} for x in m.color_attributes],'materials':[x.name for x in m.materials]}
 print(info);report.append(info)
json.dump(report,open(D+'/source-equivalence-intake.json','w'),indent=2)
