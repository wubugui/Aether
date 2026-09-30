import bpy,json,collections,os
D='/workspace/scratch/a29d03198654/Aether/source-assets/lake48';j=json.load(open(D+'/base47.json'));out=[]
for name,r in j['meshes'].items():
 f=(D+'/original_'+name.replace('massif_','')+'.blend') if name.startswith('massif') else '/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake-source-intake/'+name+'.blend'
 bpy.ops.wm.open_mainfile(filepath=f);o=next(o for o in bpy.data.objects if o.type=='MESH');m=o.data;m.calc_loop_triangles();a=r['origin']
 def v(i):
  p=o.matrix_world@m.vertices[i].co;return [p.x+a[0],p.z+a[1],-p.y+a[2]]
 def k(t):return tuple(sorted(tuple(round(x,3) for x in p) for p in t))
 b=collections.Counter(k(r['faces'][i:i+3]) for i in range(0,len(r['faces']),3));s=collections.Counter(k([v(i) for i in t.vertices]) for t in m.loop_triangles)
 from mathutils.kdtree import KDTree
 kd=KDTree(len(r["faces"]))
 for i,p in enumerate(r["faces"]):kd.insert(p,i)
 kd.balance()
 ds=[kd.find(v(i))[2] for i in range(len(m.vertices))]
 mapped=[list(kd.find(v(i))[0]) for i in range(len(m.vertices))]
 sm=collections.Counter(k([mapped[i] for i in t.vertices]) for t in m.loop_triangles)
 print("TOPOLOGY",name,sm==b, sum((sm-b).values()))
 print(name,v(0),r["faces"][0],max(ds))
 out.append({"max_nearest_vertex_distance":max(ds),'name':name,'triangles_source':sum(s.values()),'triangles_saved':sum(b.values()),'match':s==b,'unmatched_source':sum((s-b).values()),'unmatched_saved':sum((b-s).values()),'z_min':min(v.co.z for v in m.vertices),'z_max':max(v.co.z for v in m.vertices)})
json.dump(out,open(D+'/source-equivalence.json','w'),indent=2)
