def asset_world_triangles(path):
 data=path.read_bytes();i=12;doc=None;binary=None
 while i<len(data):
  n,k=struct.unpack_from('<II',data,i);chunk=data[i+8:i+8+n];i+=8+n
  if k==0x4e4f534a:doc=json.loads(chunk)
  elif k==0x004e4942:binary=chunk
 def acc(i):
  a=doc['accessors'][i];bv=doc['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']];nc={'SCALAR':1,'VEC3':3}[a['type']];stride=bv.get('byteStride',np.dtype(dt).itemsize*nc)
  return np.ndarray((a['count'],nc),dtype=dt,buffer=binary,offset=bv.get('byteOffset',0)+a.get('byteOffset',0),strides=(stride,np.dtype(dt).itemsize)).copy()
 def local(n):
  if 'matrix' in n:return np.array(n['matrix']).reshape(4,4,order='F')
  x,y,z,w=n.get('rotation',[0,0,0,1]);rot=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]);m=np.eye(4);m[:3,:3]=rot@np.diag(n.get('scale',[1,1,1]));m[:3,3]=n.get('translation',[0,0,0]);return m
 tris=[]
 def visit(i,parent):
  node=doc['nodes'][i];m=parent@local(node)
  if 'mesh' in node:
   for prim in doc['meshes'][node['mesh']]['primitives']:
    assert prim.get('mode',4)==4;x=acc(prim['attributes']['POSITION']);x=(np.column_stack([x,np.ones(len(x))])@m.T)[:,:3];x=x[:,[0,2,1]]*np.array([1,-1,1]);ix=acc(prim['indices']).ravel().reshape(-1,3);tris.extend(x[ix])
  for j in node.get('children',[]):visit(j,m)
 for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i,np.eye(4))
 return np.array(tris)
