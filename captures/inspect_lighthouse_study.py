"""Read actual exported geometry and material contracts, including node transforms."""
from pathlib import Path
import struct,json,hashlib,argparse
import numpy as np
from scipy.spatial.transform import Rotation
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('labels',nargs='*',default=['19a','19b','19c'])
parser.add_argument('--output',default='round-19abc-export-inspection.json')
args=parser.parse_args()
output=root/'reviews'/args.output
assert not output.exists()
results=[]
for label in args.labels:
    source=root/'captures'/('lighthouse_study_'+label)/'lighthouse.glb'
    raw=source.read_bytes();length,kind=struct.unpack_from('<II',raw,12)
    assert kind==0x4e4f534a
    doc=json.loads(raw[20:20+length]);binary=raw[28+length:]
    def positions(index):
        a=doc['accessors'][index];assert a['componentType']==5126 and a['type']=='VEC3' and 'sparse' not in a
        v=doc['bufferViews'][a['bufferView']]
        return np.ndarray((a['count'],3),dtype='<f4',buffer=binary,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',12),4)).copy()
    points=[];names=[]
    def visit(index,parent):
        node=doc['nodes'][index]
        if 'matrix' in node:m=np.array(node['matrix']).reshape(4,4).T
        else:
            m=np.eye(4);m[:3,:3]=Rotation.from_quat(node.get('rotation',[0,0,0,1])).as_matrix() @ np.diag(node.get('scale',[1,1,1]));m[:3,3]=node.get('translation',[0,0,0])
        world=parent @ m
        if 'mesh' in node:
            names.append(node.get('name'))
            for primitive in doc['meshes'][node['mesh']]['primitives']:
                p=positions(primitive['attributes']['POSITION'])
                transformed=(np.column_stack((p,np.ones(len(p)))) @ world.T)[:,:3]
                points.append(transformed)
                if transformed[:,1].min()<-.001 and label not in ('19g','19h'):print('BELOW ORIGIN',label,node.get('name'),transformed.min(axis=0).tolist())
        for child in node.get('children',[]):visit(child,world)
    for node in doc['scenes'][doc.get('scene',0)]['nodes']:visit(node,np.eye(4))
    p=np.vstack(points);bounds=[p.min(axis=0).tolist(),p.max(axis=0).tolist()]
    materials=[]
    for m in doc.get('materials',[]):
        if 'glass' in m['name'].lower() or 'glazing' in m['name'].lower():
            materials.append({'name':m['name'],'alpha_mode':m.get('alphaMode','OPAQUE'),'base_color':m.get('pbrMetallicRoughness',{}).get('baseColorFactor',[1,1,1,1])})
    expected=24.5 if label in ('19c','19d','19e','19f','19g','19h') else 28.1
    bottom=-.5 if label in ('19g','19h') else 0.
    checks={'height_max_matches':abs(bounds[1][1]-expected)<.001,'footing_bottom_matches':abs(bounds[0][1]-bottom)<.001}
    if label!='19a':assert all(m['alpha_mode']=='BLEND' and m['base_color'][3]<.3 for m in materials)
    results.append({'label':label,'checks':checks,'passed':all(checks.values()),'glb_sha256':hashlib.sha256(raw).hexdigest(),'mesh_nodes':len(names),'bounds_godot_m':bounds,'height_m':bounds[1][1]-bounds[0][1],'max_width_m':max(bounds[1][0]-bounds[0][0],bounds[1][2]-bounds[0][2]),'glazing':materials})
output.write_text(json.dumps({'scope':'Actual GLB node-transformed bounds and material alpha only; not collision or visual acceptance.','passed':all(r['passed'] for r in results),'results':results},indent=2))
print(json.dumps(results,indent=2))
raise SystemExit(0 if all(r['passed'] for r in results) else 1)
