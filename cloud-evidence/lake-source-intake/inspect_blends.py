import bpy,json,glob,os
out=[]
for f in glob.glob('/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake-source-intake/*.blend'):
 bpy.ops.wm.open_mainfile(filepath=f)
 row={'file':f,'objects':[]}
 for o in bpy.data.objects:
  if o.type=='MESH':
   pts=[o.matrix_world@v.co for v in o.data.vertices]
   row['objects'].append({'name':o.name,'vertices':len(pts),'polygons':len(o.data.polygons),'bounds_blender':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],'materials':[s.name for s in o.data.materials]})
 out.append(row)
json.dump(out,open('/workspace/scratch/a29d03198654/Aether/cloud-evidence/lake-source-intake/blend-inventory.json','w'),indent=2)
