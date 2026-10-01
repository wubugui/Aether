import bpy,json,struct,collections,hashlib,shutil
from pathlib import Path
from mathutils import Vector
R=Path('/workspace/scratch/a29d03198654/Aether');D=R/'source-assets/lake-cirque54/v2/final-source';S=D.parent/'attempt-e';I=R/'source-assets/lake-cirque54/intake';orig=json.load(open(D.parent/'native-authority/cirque-native-authority.json'));ORG=orig['origin'];attrs=json.load(open(I/'cirque-saved53-native-attributes.json'));rows=attrs['surfaces'][0]['expanded_attributes'];intake=json.load(open(D.parent/'native-authority/upper-remesh-intake-c.json'))
def bits(p):return struct.pack('<fff',*p)
def tri_key(t):return tuple(sorted(bits(p) for p in t))
def w(p):return [p.x+ORG[0],p.z+ORG[1],-p.y+ORG[2]]
def native(v):return list(struct.unpack('<fff',struct.pack('<fff',*v)))
attribute_triangles={}
for i in range(0,len(rows),3):
 tri=[native(r['position']) for r in rows[i:i+3]];attribute_triangles[tri_key(tri)]=list(zip(tri,[r['color'] for r in rows[i:i+3]]))
protected=[]
for rec in intake['protected_faces']:
 fi=rec['original_triangle'];tri=orig['faces'][fi*3:fi*3+3];protected.append((tri,attribute_triangles[tri_key(tri)],fi))
def bary(x,z,tri):
 a,b,c=tri;den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2]);u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den;v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den;return [u,v,1-u-v]
bpy.ops.wm.open_mainfile(filepath=str(S/'massif_cirque_wall_cirque54v2.blend'));body=bpy.data.objects['remodeled_cirque_body'];m=body.data;col=m.color_attributes.active_color;wet=0;locked=0
for poly in m.polygons:
 vv=[w(m.vertices[i].co) for i in poly.vertices];key=tri_key(vv)
 if min(p[1] for p in vv)<=0:
  src=attribute_triangles[key];wet+=1
  for li,p in zip(poly.loop_indices,vv):col.data[li].color=next(c for q,c in src if bits(q)==bits(p))
 else:
  center=[sum(p[k] for p in vv)/3 for k in range(3)]
  for tri,src,fi in protected:
   if min(bary(center[0],center[2],tri))< -1e-7:continue
   # Original flat face vertex colors are constant; interpolation also handles
   # any original nonconstant face colors without inventing a replacement.
   colors=[next(c for q,c in src if bits(q)==bits(p)) for p in tri]
   assert all(min(bary(p[0],p[2],tri))>-1e-5 for p in vv),('protected face-crossing',fi,vv)
   for li,p in zip(poly.loop_indices,vv):
    weights=bary(p[0],p[2],tri);col.data[li].color=[sum(weights[j]*colors[j][k] for j in range(3)) for k in range(4)]
   locked+=1;break
assert wet==432
payload=json.load(open(S/'cirque54v2-payload.json'));components=payload['mountains'][0]['components'];merged=[]
for c in components:
 o=bpy.data.objects[c['name']];mesh=o.data;mesh.calc_loop_triangles();attr=mesh.color_attributes.active_color;ff=[];cc=[]
 for t in mesh.loop_triangles:
  for vi,li in zip(reversed(t.vertices),reversed(t.loops)):ff.append(w(mesh.vertices[vi].co));cc.append(list(attr.data[li].color))
 assert collections.Counter(tri_key(c['vertices'][i:i+3]) for i in range(0,len(c['vertices']),3))==collections.Counter(tri_key(ff[i:i+3]) for i in range(0,len(ff),3))
 c['vertices']=ff;c['colors']=cc;merged+=ff
payload['mountains'][0]['collision_vertices']=merged
bpy.ops.wm.save_as_mainfile(filepath=str(D/'massif_cirque_wall_cirque54v2.blend'));bpy.ops.export_scene.gltf(filepath=str(D/'massif_cirque_wall_cirque54v2.glb'),export_format='GLB',export_draco_mesh_compression_enable=False,export_yup=True,export_cameras=False,export_lights=False)
json.dump(payload,open(D/'cirque54v2-payload.json','w'));shutil.copy2(S/'surface-and-wet-ledger.json',D/'surface-and-wet-ledger.json');shutil.copy2(S/'sculpt-report.json',D/'sculpt-report.json')
json.dump({'geometry_unchanged_from_closed_attempt_c':True,'wet_original_faces_color_preserved':wet,'remeshed_triangles_on_protected_original_faces_color_preserved':locked,'source_native_mesh_sha256':attrs['source_sha256'],'input_blend_sha256':hashlib.sha256((S/'massif_cirque_wall_cirque54v2.blend').read_bytes()).hexdigest(),'output_blend_sha256':hashlib.sha256((D/'massif_cirque_wall_cirque54v2.blend').read_bytes()).hexdigest()},open(D/'native-color-preservation.json','w'),indent=2)
print('CIRQUE54V2_COLOR_FINALIZED wet',wet,'protected',locked)
