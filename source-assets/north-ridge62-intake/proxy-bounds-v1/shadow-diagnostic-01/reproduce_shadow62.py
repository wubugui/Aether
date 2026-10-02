#!/usr/bin/env python3
"""Pure source-bound replay of the actual first-mesh failure. Default prints only."""
from pathlib import Path
import argparse,collections,hashlib,json,math,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parents[1]/'scatter-readonly-v1'))
from decoder62 import read_rsrc
P=ROOT/'candidates/round40-exclusive-20260930/project'
NATIVE=ROOT/'cloud-evidence/north-ridge62-proxy-version-v2-20261002T085042Z-fb_yi_2s/native-proxy-meshes.json'

def require(ok,label):
    if not ok:raise ValueError(label)
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pinned():
    pins=json.loads((HERE/'INPUTS.json').read_text())
    for rel,pin in pins.items():
        path=ROOT/rel;require(path.stat().st_size==pin['bytes']and digest(path)==pin['sha256'],'pinned input changed '+rel)
    return pins

def vector_sha(vertices):return hashlib.sha256(b''.join(struct.pack('<3f',*v)for v in vertices)).hexdigest()
def extrema(vertices):return {'min':[min(v[a]for v in vertices)for a in range(3)],'max':[max(v[a]for v in vertices)for a in range(3)]}
def native_box(b):return {k:[f32(x)for x in b[k]]for k in ['min','max']}
def oriented(faces):
    require(len(faces)%3==0,'triangle count')
    return collections.Counter(min(tuple(faces[i+j:i+3]+faces[i:i+j])for j in range(3))for i in range(0,len(faces),3))
def decode(raw,surface):
    # Exact narrow compressed-position branch from the already checked
    # visible_geometry61.gd surface_positions. Binary framing is the old decoder.
    fmt=surface['format'];require(fmt in [34896613377,34896613407],'unexpected diagnostic format')
    n=surface['vertex_count'];a=surface['aabb']['values'];d=surface['vertex_data'];data=raw[d['payload_offset']:d['payload_offset']+d['payload_bytes']]
    require(len(data)==n*(8 if fmt==34896613377 else 12),'position/normal storage length')
    vertices=[tuple(f32(f32(f32(q/65535.0)*a[j+3])+a[j])for j,q in enumerate(struct.unpack_from('<3H',data,i*8)))for i in range(n)]
    def faces(payload):
        ib=raw[payload['payload_offset']:payload['payload_offset']+payload['payload_bytes']]
        require(len(ib)%6==0 and n<=65536,'index layout')
        indices=struct.unpack('<'+'H'*(len(ib)//2),ib);require(all(i<n for i in indices),'index range')
        return [vertices[i]for i in indices]
    levels={0.0:faces(surface['index_data'])};lods=surface.get('lods',[]);require(len(lods)%2==0,'LOD pairs')
    for threshold,indices in zip(lods[::2],lods[1::2]):
        require(threshold>max(levels),'LOD order');levels[threshold]=faces(indices)
    return vertices,levels

def mesh_pair(path):
    raw=path.read_bytes();doc=read_rsrc(path);meshes=[r for r in doc['resources']if r['type']=='ArrayMesh']
    require(len(meshes)==2,'expected primary/shadow pair')
    primary=meshes[-1];shadow=doc['resources'][primary['properties']['shadow_mesh']['index']]
    require(len(primary['properties']['_surfaces'])==len(shadow['properties']['_surfaces'])==1,'one surface each')
    v,levels=decode(raw,primary['properties']['_surfaces'][0]);sv,sl=decode(raw,shadow['properties']['_surfaces'][0])
    require(levels.keys()==sl.keys(),'all LOD threshold identities')
    require(all(oriented(levels[t])==oriented(sl[t])for t in levels),'all exact oriented triangle multisets')
    summary={'resource':str(path.relative_to(ROOT)),'source_sha256':digest(path),'primary_id':primary['path'],'shadow_id':shadow['path'],
             'primary_vertices':len(v),'shadow_vertices':len(sv),'primary_vertex_sha256':vector_sha(v),'shadow_vertex_sha256':vector_sha(sv),
             'base_face_vertex_count':len(levels[0.]),'oriented_triangles':len(levels[0.])//3,'base_indexed_faces_sha256':vector_sha(levels[0.]),
             'shadow_base_indexed_faces_sha256':vector_sha(sl[0.]),'all_level_thresholds':list(levels),'all_levels_exact_oriented_multiset_equal':True,
             'primary_vertex_bounds':extrema(v),'shadow_vertex_bounds':extrema(sv)}
    return summary,v,levels[0.]

def reproduce():
    pins=pinned();native=json.loads(NATIVE.read_text());require(native['engine_version_guard']['passed']is True and native['issues']==['native arrays unavailable'],'failure identity')
    require(len(native['visual_meshes'])==1,'one partial primary observation')
    item=native['visual_meshes'][0];pair,vertices,faces=mesh_pair(P/'assets/coast61/oak_-5_-5_CoastalPines36b.res')
    require(vector_sha(vertices)==item['surfaces'][0]['vertex_bytes_sha256'],'entire decoded primary byte hash equals native')
    require(extrema(vertices)==native_box(item['vertex_bounds']),'actual primary extrema match exact float32')
    step=f32(.0001)
    snapped=[tuple(f32(math.floor(f32(f32(x/step)+f32(.5)))*step)for x in v)for v in faces]
    require(vector_sha(snapped)==item['face_bytes_sha256'],'entire snapped indexed-face byte hash equals actual get_faces')
    require(extrema(snapped)==native_box(item['face_bounds']),'all actual get_faces extrema match')
    require(len(faces)==item['face_vertex_count']==168 and len(vertices)==120 and pair['shadow_vertices']==36,'exact fixture counts')
    classes=[mesh_pair(P/f'assets/meshes/{kind}.res')[0]for kind in ['pine','oak','poplar','rock','bush']]
    require(pins==pinned(),'inputs unchanged during replay')
    return {'status':'exact_offline_reproduction_of_first_native_mesh_failure','native_report_sha256':digest(NATIVE),
            'engines_started':0,'source_or_failed_evidence_modified':False,'runtime_collision_observed':False,'all_occupancy_complete':False,
            'first_mesh_pair':pair,'native_primary_vertex_hash_exact':True,'native_get_faces_full_byte_hash_exact':True,
            'native_get_faces_sha256':vector_sha(snapped),'native_get_faces_bounds':extrema(snapped),'step_float32':step,
            'step_float32_hex':struct.pack('<f',step).hex(),'snapping_formula':'f32(floor(f32(f32(x/f32(0.0001))+f32(0.5)))*f32(0.0001))',
            'bound_delta_get_faces_minus_native_vertices':{k:[extrema(snapped)[k][a]-extrema(vertices)[k][a]for a in range(3)]for k in ['min','max']},
            'interpretation':'The actual API primary vertices exactly match the narrow compressed decoder. Their get_faces differences are exactly reproduced by the established 0.1mm float32 snapping path; no epsilon is needed. This is an exact replay for these fixed inputs, not a general new engine implementation proof.',
            'shadow_api_issue':'Position-only compressed shadow format 34896613377 omits the normal flag; the existing strict native audit permits only the known null ARRAY_VERTEX branch and decodes actual packed payload, requiring exact main/shadow oriented coverage at base and every LOD.',
            'canonical_class_shadow_replay':classes,'reused_native_helper_sha256':digest(ROOT/'source-assets/coast61-nearbay-orbit/visible_geometry61.gd')}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();value=reproduce();data=json.dumps(value,indent=2)+'\n'
    if args.write:(HERE/'DIAGNOSIS.json').write_text(data)
    print(data,end='')
