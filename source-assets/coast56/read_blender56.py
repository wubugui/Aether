import bpy,json,numpy as np,hashlib,sys
from pathlib import Path
D=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
objname=args[0] if args else 'Ground_-4_-4_AUTHORITY';destination=args[1] if len(args)>1 else 'zero-change-readback.json'
obj=bpy.data.objects[objname];m=obj.data;n=len(m.vertices)
p=np.empty(n*3,np.float32);m.vertices.foreach_get('co',p);p=p.reshape(-1,3);pos=np.column_stack((p[:,0],p[:,2],-p[:,1])).astype(np.float32)
idx=np.asarray([list(poly.vertices)[0:1]+list(poly.vertices)[2:3]+list(poly.vertices)[1:2] for poly in m.polygons],np.int32).reshape(-1)
normal=np.empty(n*3,np.float32);m.attributes['godot_normal'].data.foreach_get('vector',normal);normal=normal.reshape(-1,3)
tan=np.empty(n*3,np.float32);m.attributes['godot_tangent_xyz'].data.foreach_get('vector',tan);w=np.empty(n,np.float32);m.attributes['godot_tangent_w'].data.foreach_get('value',w);tan=np.column_stack((tan.reshape(-1,3),w)).astype(np.float32).reshape(-1)
col=np.empty(n*4,np.float32);m.color_attributes['NativeColor'].data.foreach_get('color',col);col=col.reshape(-1,4)
arrays=[pos.tolist(),normal.tolist(),tan.tolist(),col.tolist(),None,None,None,None,None,None,None,None,idx.tolist()]
source=json.loads((D/'native-authority/authority.json').read_text())
checks={}
for k in [0,1,2,3,12]:
 typ=np.int32 if k==12 else np.float32
 old=np.asarray(source['surfaces'][0]['arrays'][k],typ);new=np.asarray(arrays[k],typ)
 checks[str(k)]={'exact_float32_or_int32_equal':old.shape==new.shape and old.tobytes()==new.tobytes(),'sha256':hashlib.sha256(new.tobytes()).hexdigest(),'shape':list(new.shape)}
out={'blend':bpy.data.filepath,'object':objname,'source_sha256':source['source_sha256'],'origin':[-3072,0,-3072],'arrays':arrays,'authority_field_checks':checks,'world_matrix':list(sum((list(row) for row in obj.matrix_world),[]))}
(D/destination).write_text(json.dumps(out,separators=(',',':')))
print('BLENDER56_READBACK',objname,json.dumps(checks))
if objname.endswith('AUTHORITY') and not all(v['exact_float32_or_int32_equal'] for v in checks.values()):raise RuntimeError('Zero-change native field preservation failed')
