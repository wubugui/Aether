"""Pure export/import contract. No engine work or filesystem writes on import."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import struct
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
K=HERE.parent
SOURCE=K/'recovery-01/authored_envelope58k.blend'
SOURCE_SHA='16eeb67dce6e89f05562b67f869c77dd7882942585241a2648ae46ff48012bee'
EVIDENCE=ROOT/'cloud-evidence/cloudbank58k-recovery01-20261002T075038Z-4xi10wm2'
BANK='CloudBank58K_authored_polyhedral_shell'
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
GODOT=ROOT.parent/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
BLENDER_SHA='050c02562f81fe80ba616a80198fa02d381e60f8b61b8d39add881f4bca0d7d8'
GODOT_SHA='db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
FRAME=K.parent/'revision-d/control-plan58d.json'
SETTINGS=K.parent/'revision-d/native-01/preview-settings58d.json'
MAP=np.array([[1.,0.,0.],[0.,0.,1.],[0.,-1.,0.]])
POSITION_EPS=1e-5
NORMAL_EPS=3e-5
MAX_GLB_BYTES=250000

def require(ok,message):
    if not ok:raise ValueError(message)

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def load(path):
    spec=importlib.util.spec_from_file_location(path.stem+'_import58k',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def strict_json_text(text):
    def unique(rows):
        result={}
        for k,v in rows:
            require(k not in result,'Duplicate JSON key');result[k]=v
        return result
    def bad(v):raise ValueError('Nonfinite JSON number '+v)
    value=json.loads(text,object_pairs_hook=unique,parse_constant=bad)
    def finite(v):
        if isinstance(v,float):require(math.isfinite(v),'Nonfinite float')
        elif isinstance(v,dict):
            for x in v.values():finite(x)
        elif isinstance(v,list):
            for x in v:finite(x)
    finite(value);return value

def read(path):return strict_json_text(Path(path).read_text())

def write(path,value):
    require(not Path(path).exists(),'Never replace evidence '+str(path))
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def geometry_fingerprint(v,f):
    return dict(vertices_sha256=hashlib.sha256(np.asarray(v,dtype='<f8').tobytes()).hexdigest(),faces_sha256=hashlib.sha256(np.asarray(f,dtype='<i4').tobytes()).hexdigest())

def mapped(v):return np.asarray(v,float)@MAP.T

def bounds(v):
    v=np.asarray(v,float);return [v.min(axis=0).tolist(),v.max(axis=0).tolist()]

def source_preconditions():
    require(SOURCE.is_file() and SOURCE.stat().st_size==136389 and sha(SOURCE)==SOURCE_SHA,'Accepted source identity changed')
    verified=read(EVIDENCE/'outputs/saved-source-verify58k.json')
    contact=read(EVIDENCE/'outputs/saved-source-contact58k.json')
    require(verified['passed'] and verified['saved_source_validated'] and verified['source_unchanged'] and verified['source_sha256']==SOURCE_SHA,'Source verification missing')
    require(contact['passed'] and contact['actual_saved_source_arrays'] and contact['source_sha256_before']==SOURCE_SHA and contact['source_sha256_after']==SOURCE_SHA,'Actual-saved-array contact proof missing')
    require(contact['native_array_fingerprint']==verified['native_identity']['mesh'],'Saved-array evidence mismatch')
    entry=load(K/'recovery-01/source_contact58k.py')
    entry.verify_original_inputs()
    entry.guard.validate_contact(contact,verified,SOURCE_SHA,sha(EVIDENCE/'outputs/saved-source-verify58k.json'),entry.code_identities())
    return verified

def parse_glb(path):
    require(20<=Path(path).stat().st_size<=MAX_GLB_BYTES,'GLB size budget before read')
    with Path(path).open('rb') as stream:data=stream.read(MAX_GLB_BYTES+1)
    return parse_glb_bytes(data)

def parse_glb_bytes(data):
    require(20<=len(data)<=MAX_GLB_BYTES,'GLB size budget')
    magic,version,total=struct.unpack_from('<4sII',data)
    require((magic,version,total)==(b'glTF',2,len(data)),'GLB header')
    chunks=[];offset=12
    while offset<len(data):
        require(offset+8<=len(data),'GLB truncated chunk header')
        length,kind=struct.unpack_from('<I4s',data,offset);offset+=8
        require(length%4==0 and offset+length<=len(data),'GLB chunk extent')
        chunks.append((kind,data[offset:offset+length]));offset+=length
    require([r[0] for r in chunks]==[b'JSON',b'BIN\x00'],'Exactly JSON plus embedded BIN')
    document=strict_json_text(chunks[0][1].decode());binary=chunks[1][1]
    require(document.get('asset',{}).get('version')=='2.0','glTF version')
    for key in ('images','textures','samplers','skins','animations','cameras','extensionsUsed','extensionsRequired'):
        require(not document.get(key),'Unexpected glTF '+key)
    require(len(document.get('buffers',[]))==1 and not document['buffers'][0].get('uri'),'Embedded buffer only')
    require(0<=len(binary)-document['buffers'][0]['byteLength']<=3,'BIN padding')
    require(len(document.get('nodes',[]))==1 and len(document.get('meshes',[]))==1,'One selected mesh only')
    node=document['nodes'][0]
    require(node.get('mesh')==0 and node.get('name')==BANK and not node.get('children'),'Selected mesh node identity')
    require(node.get('translation',[0,0,0])==[0,0,0] and node.get('scale',[1,1,1])==[1,1,1] and node.get('rotation',[0,0,0,1])==[0,0,0,1],'No origin or basis rewrite')
    require(node.get('matrix',[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1])==[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],'Identity node matrix')
    scenes=document.get('scenes',[])
    require(document.get('scene',0)==0 and len(scenes)==1 and scenes[0].get('nodes')==[0] and set(scenes[0])<={'name','nodes'},'Single scene root')
    primitive=document['meshes'][0]['primitives'];require(len(primitive)==1,'One material surface')
    p=primitive[0];require(p.get('mode',4)==4 and set(p['attributes'])=={'POSITION','NORMAL'},'Only triangle positions/normals')
    require(not p.get('targets') and not p.get('extensions'),'No morph/compression extensions')
    require(p.get('material')==0 and len(document.get('materials',[]))==1,'One neutral material')
    material=document['materials'][0];require(not material.get('extensions') and material.get('alphaMode','OPAQUE')=='OPAQUE','Plain opaque PBR material')
    def accessor(index,kind,types):
        a=document['accessors'][index];require(a['type']==kind and a['componentType'] in types,'Accessor type')
        require(not a.get('sparse') and not a.get('normalized'),'Uncompressed nonnormalized accessor')
        size={'SCALAR':1,'VEC3':3}[kind];fmt={5123:'H',5125:'I',5126:'f'}[a['componentType']];unit=struct.calcsize('<'+fmt)*size
        require(0<a['count']<=1152,'Accessor count budget')
        view=document['bufferViews'][a['bufferView']];require(view.get('buffer',0)==0,'Embedded buffer view')
        start=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',unit)
        require(stride>=unit and start>=view.get('byteOffset',0) and start+(a['count']-1)*stride+unit<=view.get('byteOffset',0)+view['byteLength']<=document['buffers'][0]['byteLength'],'Accessor bounds')
        result=np.asarray([struct.unpack_from('<'+fmt*size,binary,start+i*stride) for i in range(a['count'])])
        require(np.isfinite(result).all(),'Nonfinite accessor')
        if kind=='VEC3' and 'min' in a:require(np.max(np.abs(result.min(axis=0)-a['min']))<=POSITION_EPS and np.max(np.abs(result.max(axis=0)-a['max']))<=POSITION_EPS,'Accessor declared bounds')
        return result
    positions=accessor(p['attributes']['POSITION'],'VEC3',{5126})
    normals=accessor(p['attributes']['NORMAL'],'VEC3',{5126})
    indices=accessor(p['indices'],'SCALAR',{5123,5125}).ravel().astype(int)
    return document,dict(positions=positions.tolist(),normals=normals.tolist(),indices=indices.tolist()),material

def canonical(face):
    t=tuple(map(int,face));return min(t,t[1:]+t[:1],t[2:]+t[:2])

def validate_geometry(raw,source,clockwise=False):
    expected=mapped(source['positions']);faces=np.asarray(source['triangles'],int)
    v=np.asarray(raw['positions'],float);n=np.asarray(raw['normals'],float);i=np.asarray(raw['indices'],int)
    require(v.ndim==2 and v.shape[1]==3 and n.shape==v.shape and np.isfinite(v).all() and np.isfinite(n).all(),'Finite paired positions/normals')
    require(194<=len(v)<=1152 and len(i)==1152 and i.min()>=0 and i.max()<len(v),'194 authored vertices /384 triangles; bounded render split count')
    distance=np.max(np.abs(v[:,None,:]-expected[None,:,:]),axis=2);mapping=distance.argmin(axis=1);error=distance[np.arange(len(v)),mapping]
    require(float(error.max())<=POSITION_EPS and set(mapping)==set(range(194)),'Every split vertex maps to exact authored positions, no missing source point')
    require(set(i)==set(range(len(v))),'No unused render vertices')
    actual=mapping[i].reshape(-1,3)
    if clockwise:actual=actual[:,[0,2,1]]
    require(sorted(map(canonical,actual))==sorted(map(canonical,faces)),'Triangle bijection and front-face winding')
    expected_normals=np.cross(expected[faces[:,1]]-expected[faces[:,0]],expected[faces[:,2]]-expected[faces[:,0]])
    expected_normals/=np.linalg.norm(expected_normals,axis=1)[:,None]
    by_face={canonical(f):normal for f,normal in zip(faces,expected_normals)}
    require(np.max(np.abs(np.linalg.norm(n,axis=1)-1))<=(2e-4 if clockwise else NORMAL_EPS),'Unit normals')
    max_normal=0.
    normal_epsilon=2e-4 if clockwise else NORMAL_EPS # Godot's packed normals can quantize even without position compression.
    for triangle,idx in zip(actual,i.reshape(-1,3)):
        err=float(np.max(np.abs(n[idx]-by_face[canonical(triangle)])))
        require(np.max(np.abs(n[idx]-n[idx[0]]))<=1e-7,'Smooth normals replaced the flat triangle')
        require(err<=normal_epsilon,'Flat outward corner normals changed');max_normal=max(max_normal,err)
    require(np.max(np.abs(np.asarray(bounds(v))-bounds(expected)))<=POSITION_EPS,'Actual bounds unchanged')
    return dict(passed=True,authored_vertex_count=194,render_vertex_count=len(v),triangles=384,maximum_position_error_m=float(error.max()),maximum_normal_component_error=max_normal,godot_relative_bounds=bounds(v),front_face='clockwise' if clockwise else 'counterclockwise')

def linear_to_srgb(v):return 12.92*v if v<.0031308 else 1.055*(v**(1/2.4))-.055

def validate_material(material,source,godot=False):
    m=source['material'];base=m['base_color_linear_rgba']
    if godot:
        expected=[linear_to_srgb(x) for x in base[:3]]+[base[3]]
        actual=material['albedo_srgb_rgba'];rough=material['roughness'];metal=material['metallic']
        require(material['texture_count']==0 and material['shader_material']==False and material['emission_enabled']==False and material['emission_rgb']==[0,0,0],'No engine texture/shader/emission override')
        require(material['transparency']==0 and material['cull_mode']==(2 if m['double_sided'] else 0),'Imported alpha/cull state')
    else:
        require(set(material)<={'name','pbrMetallicRoughness','doubleSided','alphaMode','emissiveFactor'},'Unexpected material property')
        require(material.get('alphaMode','OPAQUE')=='OPAQUE' and material.get('emissiveFactor',[0,0,0])==[0,0,0],'Opaque non-emissive neutral material')
        require(set(material['pbrMetallicRoughness'])<={'baseColorFactor','roughnessFactor','metallicFactor'},'Unexpected PBR property')
        mr=material['pbrMetallicRoughness'];actual=mr.get('baseColorFactor',[1,1,1,1]);rough=mr.get('roughnessFactor',1);metal=mr.get('metallicFactor',1);expected=base
        require(material.get('doubleSided',False)==m['double_sided'],'glTF culling')
        require(not any('Texture' in k for k in mr) and not any('Texture' in k for k in material),'No textures')
    require(np.max(np.abs(np.asarray(actual)-expected))<=2e-6,'Material color / linear-sRGB contract')
    require(abs(rough-m['roughness'])<=1e-6 and abs(metal-m['metallic'])<=1e-6,'Material PBR factors')
    return dict(passed=True,color_representation='sRGB Godot property' if godot else 'linear glTF factor',maximum_color_error=float(np.max(np.abs(np.asarray(actual)-expected))))
