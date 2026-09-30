"""Read exported GLBs and validate actual closed geometry, independently of bpy.

Validates both kit libraries, not their visual fidelity. Handles node transforms
and accessor strides; no mesh/image files are modified.
"""
from pathlib import Path
import json,struct,collections,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[1]

def triangles(path):
    data=path.read_bytes();assert data[:4]==b'glTF'
    chunks={};offset=12
    while offset<len(data):
        length,kind=struct.unpack_from('<II',data,offset)
        chunks[kind]=data[offset+8:offset+8+length];offset+=8+length
    doc=json.loads(chunks[0x4e4f534a]);binary=chunks[0x004e4942]
    def accessor(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        dt=np.dtype({5126:'<f4',5125:'<u4',5123:'<u2',5121:'u1'}[a['componentType']])
        count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        return np.ndarray((a['count'],count),dt,buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',dt.itemsize*count),dt.itemsize)).copy()
    output=[]
    def visit(index,parent):
        node=doc['nodes'][index]
        if 'matrix' in node:local=np.asarray(node['matrix']).reshape(4,4).T
        else:
            x,y,z,w=node.get('rotation',[0,0,0,1])
            r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
                        [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
                        [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
            local=np.eye(4);local[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));local[:3,3]=node.get('translation',[0,0,0])
        world=parent@local
        if 'mesh' in node:
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode',4)==4
                p=accessor(primitive['attributes']['POSITION']).astype(float)
                p=(np.c_[p,np.ones(len(p))]@world.T)[:,:3]
                indices=accessor(primitive['indices']).ravel() if 'indices' in primitive else np.arange(len(p))
                output.append(p[indices.reshape(-1,3)])
        for child in node.get('children',[]):visit(child,world)
    for node in doc['scenes'][doc.get('scene',0)]['nodes']:visit(node,np.eye(4))
    return doc,np.concatenate(output)

results=[]
for library in ['cliff_kit','mountain_kit']:
    for item in json.loads((ROOT/'assets'/f'{library}.json').read_text()):
        path=ROOT/item['path'];doc,t=triangles(path)
        keys={};ids=[]
        for tri in t:ids.append([keys.setdefault(tuple(np.round(v,5)),len(keys)) for v in tri])
        edges=collections.Counter(tuple(sorted((a,b))) for f in ids for a,b in zip(f,f[1:]+f[:1]))
        area=np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)*.5
        volume=abs(float(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6))
        bad_edges=sum(v!=2 for v in edges.values());degenerate=int((area<1e-8).sum())
        error=abs(volume-item['volume_m3'])/item['volume_m3']
        ok=bad_edges==0 and degenerate==0 and error<.0001 and not doc.get('images') and (ROOT/item['native_source']).exists()
        result={'name':item['name'],'passed':ok,'triangles':len(t),'nonmanifold_or_open_edges':bad_edges,'degenerate_faces':degenerate,
            'volume_relative_error':error,'bounds':[t.min((0,1)).tolist(),t.max((0,1)).tolist()],
            'images':len(doc.get('images',[])),'glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        results.append(result);print('PASS' if ok else 'FAIL',item['name'],len(t),'triangles')
report={'passed':all(r['passed'] for r in results),'assets':results,
        'scope':'Independent exported-GLB manifold, degenerate triangle, native source, image absence and enclosed-volume validation. Visual acceptance is separate.'}
(ROOT/'captures/geology-asset-validation.json').write_text(json.dumps(report,indent=2))
raise SystemExit(0 if report['passed'] else 1)
