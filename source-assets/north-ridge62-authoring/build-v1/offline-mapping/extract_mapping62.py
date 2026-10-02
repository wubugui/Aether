#!/usr/bin/env python3
"""Four pinned text-literal blocks only. Offline, no engine or project writes.
Reuses reviewed HEADER/numbers/f32 helpers and the existing surface_positions
compressed-position formula. This is not a general TSCN/RSRC parser.
"""
from pathlib import Path
import argparse,base64,collections,gzip,hashlib,json,math,mmap,re,struct,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
HELPER=ROOT/'source-assets/north-ridge62-intake/scatter-readonly-v1/scene_inputs62.py'
sys.path.insert(0,str(HELPER.parent))
from scene_inputs62 import HEADER,numbers,f32,require
PROJECT=ROOT/'candidates/round40-exclusive-20260930/project'
SCENE=PROJECT/'scenes/candidate53d-west/Game53dWest.tscn'
SURVEY=ROOT/'cloud-evidence/coast-boundary-readonly-20261001/native-coast.json'
INTAKE=ROOT/'cloud-evidence/north-ridge62-collect-20261002T053100Z-3mmbw0ol/native-intake.json'
PLAN=HERE.parent.parent/'preparation-v1/candidate-plan.json'
SURVEY_SCRIPT=SURVEY.parent/'read_saved_coast.gd'
POSITION_FORMULA=ROOT/'source-assets/coast61-nearbay-orbit/visible_geometry61.gd'
COLOR_LAYOUT=ROOT/'source-assets/north-ridge62-intake/scatter-readonly-v1/upstream/drivers__gles3__storage__mesh_storage.cpp'
TARGETS={'Ground_-4_-7':'ArrayMesh_xat5f','Ground_-3_-7':'ArrayMesh_ywvy3','Ground_-4_-6':'ArrayMesh_v5uyt','Ground_-3_-6':'ArrayMesh_rlgfb'}
EXPECTED_COUNTS={'Ground_-4_-7':6144,'Ground_-3_-7':6144,'Ground_-4_-6':6058,'Ground_-3_-6':6009}
SURFACE_KEYS=['aabb','attribute_data','format','index_count','index_data','material','name','primitive','uv_scale','vertex_count','vertex_data']
PINS={SCENE:'6ec57b72a831d6fa906a8d866c339909de55c9c42297a038dcd429b18d0c2b18',SURVEY:'886c5d04611e9971d5e50675dce438df5674ce3a66f2cfa5cb569a58d5d949d0',INTAKE:'5d6e5719b9b5f22397338ab508324ec180afd5a1d54554dcb66294ed79e88df2'}
def sha(b):return hashlib.sha256(b).hexdigest()
def encode(o):return (json.dumps(o,separators=(',',':'),allow_nan=False)+'\n').encode()
def pin(path):return {'bytes':path.stat().st_size,'sha256':sha(path.read_bytes())}
def array_bytes(v):return b''.join(struct.pack('<3f',*p)for p in v)
def literals(block,rid):
    # Only the observed full one-surface line grammar. No eval, partial field
    # acceptance, unknown properties, recursively followed refs or extra surfaces.
    lines=block.decode('utf8').splitlines()
    require(lines[0]==f'[sub_resource type="ArrayMesh" id="{rid}"]','wrong header')
    require(re.fullmatch(r'resource_name = "[^"\\]*"',lines[1]),'unsupported resource name')
    require(lines[2]=='_surfaces = [{' and lines[14]=='}]' and lines[15]=='blend_shape_mode = 0','unsupported one-surface framing')
    if rid in ['ArrayMesh_xat5f','ArrayMesh_ywvy3']:
        require(re.fullmatch(r'shadow_mesh = SubResource\("[A-Za-z0-9_]+"\)',lines[16]),'unsupported shadow reference')
        require(all(not l for l in lines[17:]),'unread trailing properties')
    else:
        require(all(not l for l in lines[16:]),'unexpected trailing properties')
    result={}
    for key,line in zip(SURFACE_KEYS,lines[3:14]):
        m=re.fullmatch(r'"'+key+r'": (.+)'+(','if key!='vertex_data'else''),line)
        require(m is not None,'unsupported/duplicate/reordered field '+key);result[key]=m[1]
    require(result['format']=='34896613391' and result['primitive']=='3','unsupported format/primitive')
    require(re.fullmatch(r'SubResource\("[A-Za-z0-9_]+"\)',result['material']),'unsupported material')
    require(re.fullmatch(r'"[^"\\]*"',result['name']),'unsupported surface name')
    require(numbers(result['uv_scale'],'Vector4',4)==[0.,0.,0.,0.],'unexpected UV scale')
    return result

def packed(raw):
    m=re.fullmatch(r'PackedByteArray\("([A-Za-z0-9+/=]*)"\)',raw)
    require(m is not None,'unsupported PackedByteArray encoding')
    value=base64.b64decode(m[1],validate=True)
    require(base64.b64encode(value).decode()==m[1],'noncanonical base64')
    return value

def build(write=False):
    tracked=[SCENE,SURVEY,INTAKE,PLAN,SURVEY_SCRIPT,HELPER,POSITION_FORMULA,COLOR_LAYOUT]
    before={str(p.relative_to(ROOT)):pin(p)for p in tracked}
    for p,s in PINS.items():require(before[str(p.relative_to(ROOT))]['sha256']==s,'source pin changed '+str(p))
    survey=json.loads(SURVEY.read_text());intake=json.loads(INTAKE.read_text());plan=json.loads(PLAN.read_text())
    require(survey['source_sha256']==PINS[SCENE] and intake['scene_sources'][survey['source']]==PINS[SCENE],'native scene binding')
    for p in [SURVEY,INTAKE]:require(plan['source_pins'][str(p.relative_to(ROOT))]==before[str(p.relative_to(ROOT))],'plan binding')
    require(intake['saved_data_read_complete']is True and intake['issues']==[],'native intake incomplete')
    script=SURVEY_SCRIPT.read_text()
    require('var a=n.mesh.surface_get_arrays(s)'in script and 'for index in indices:faces.append(vec(t*vertices[index]))'in script,'survey method changed')
    records=[];artifacts={}
    with SCENE.open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as raw:
      for name,rid in TARGETS.items():
        marker=f'[sub_resource type="ArrayMesh" id="{rid}"]'.encode();start=raw.find(marker)
        require(start>=0 and raw.find(marker,start+1)==-1,'missing/duplicate selected resource')
        endmatch=HEADER.search(raw,start+len(marker));require(endmatch is not None,'missing block end');end=endmatch.start();block=raw[start:end]
        fields=literals(block,rid)
        n=int(fields['vertex_count']);ic=int(fields['index_count']);require(n==EXPECTED_COUNTS[name] and ic==6144,'unexpected counts')
        blobs={k:packed(fields[k])for k in ['vertex_data','attribute_data','index_data']}
        require(len(blobs['vertex_data'])==n*12 and len(blobs['attribute_data'])==n*4 and len(blobs['index_data'])==ic*2,'storage lengths')
        aabb=numbers(fields['aabb'],'AABB',6);require(all(x>=0 for x in aabb[3:]),'negative AABB')
        indices=list(struct.unpack('<'+'H'*ic,blobs['index_data']));require(max(indices)<n,'index out of bounds')
        positions=[[f32(f32(f32(q/65535.0)*aabb[j+3])+aabb[j])for j,q in enumerate(struct.unpack_from('<3H',blobs['vertex_data'],i*8))]for i in range(n)]
        prior=next(t for t in intake['terrain']if t['tile']==name)
        source=next(t for t in survey['terrain']if t['node']==prior['geometry']['record_node'])
        require(prior['resource']==source['mesh']==survey['source']+'::'+rid,'resource mismatch')
        require(prior['same_bound_resource_and_transform_as_sha_pinned_53d']is True,'native reuse mismatch')
        tb=bytes.fromhex(prior['transform_hex']);require(len(tb)==52 and struct.unpack_from('<I',tb)[0]==18,'transform encoding')
        t=list(struct.unpack_from('<12f',tb,4));require(t[:9]==[1.,0.,0.,0.,1.,0.,0.,0.,1.] and t[9:]==source['origin'],'only verified identity+translation supported')
        world=[[f32(p[j]+t[j+9])for j in range(3)]for p in positions]
        expanded=[world[i]for i in indices];native=[[f32(x)for x in v]for v in source['faces']]
        require(len(native)==ic and array_bytes(expanded)==array_bytes(native),'ordered float32 world survey mismatch')
        reverse=[[]for _ in range(n)]
        for corner,i in enumerate(indices):reverse[i].append(corner)
        require(all(reverse),'unexpected unreferenced source vertex')
        colors=[list(blobs['attribute_data'][i*4:(i+1)*4])for i in range(n)]
        rows=[]
        for i,p in enumerate(positions):
          rows.append({'source_vertex':i,'source_local_xyz':p,'world_xyz_float32':world[i],
                       'survey_expanded_corners':reverse[i],
                       'survey_world_xyz_json':source['faces'][reverse[i][0]],
                       'survey_face_corners':[[k//3,k%3]for k in reverse[i]],
                       'source_color_rgba8':colors[i],
                       'source_color_rgba_normalized_float32':[f32(c/255.)for c in colors[i]]})
        decimal_error=max(abs(source['faces'][i][j]-expanded[i][j])for i in range(ic)for j in range(3))
        roundoff=max(abs((positions[i][j]+t[j+9])-world[i][j])for i in range(n)for j in range(3))
        record={'tile':name,'resource':prior['resource'],'surface':0,'format':34896613391,'format_hex':'0x82000100f',
                'format_fields':['vertex','normal','tangent','color','index','compressed_attributes','current_format_version'],
                'vertex_count':n,'index_count':ic,'triangle_count':ic//3,'indices_sequential':indices==list(range(n)),
                'unique_local_xyz_count':len(set(map(tuple,positions))),'unique_world_xyz_count':len(set(map(tuple,world))),
                'source_block_byte_span':[start,end],'source_block_sha256':sha(block),
                'surface_storage_sha256_native_intake_witness':prior['surface_storage_sha256'],
                'surface_storage_variant_hash_recomputed':False,
                'source_aabb':aabb,'world_transform_columns':t,'transform_variant_hex':prior['transform_hex'],
                'source_material_reference':fields['material'],'source_surface_name':json.loads(fields['name']),
                'source_shadow_reference':block.decode().splitlines()[16].split(' = ',1)[1]if block.decode().splitlines()[16]else None,
                'source_uv_present':False,'source_uv2_present':False,'source_colors_present':True,
                'source_color_storage':'one RGBA8 unsigned normalized record per original source vertex',
                'packed_payloads':{k:{'bytes':len(v),'sha256':sha(v),'file':name+'.'+k+'.bin'}for k,v in blobs.items()},
                'position_storage':{'start':0,'stride':8,'bytes':n*8,'xyz':'u16x3 normalized by 65535, float32 AABB decode','fourth_u16':'preserved uninterpreted packed tangent component'},
                'normal_tangent_storage':{'start':n*8,'stride':4,'bytes':n*4,'semantic_decode_performed':False},
                'survey_method':'surface_get_arrays; index expansion in source order; float32 composed world transform; no Mesh.get_faces; no snapping; no nearest match',
                'survey_node':source['node'],'survey_ordered_float32_match':True,
                'survey_ordered_world_xyz_float32_sha256':sha(array_bytes(expanded)),
                'source_local_xyz_float32_sha256':sha(array_bytes(positions)),
                'float32_max_component_error_m':0.0,'survey_json_decimal_vs_float32_max_error_m':decimal_error,
                'float32_translation_max_roundoff_m':roundoff,
                'stored_position_quantization_step_m':[x/65535. for x in aabb[3:]],
                'mapping_file':name+'.mapping.json.gz'}
        mapping={'schema':'north62_four_mesh_original_index_mapping_v1','source':record,'source_vertices':rows,'index_sequence':indices,
                 'corner_formula':'For expanded corner k, face=k//3, corner=k%3, source vertex=index_sequence[k]. No positional welding.'}
        packed_map=gzip.compress(encode(mapping),mtime=0)
        contents={name+'.mapping.json.gz':packed_map,name+'.source-block.tscn.txt':block}
        contents.update({name+'.'+k+'.bin':v for k,v in blobs.items()})
        for fn,data in contents.items():
          artifacts[fn]={'bytes':len(data),'sha256':sha(data)}
          if write:(HERE/fn).write_bytes(data)
        records.append(record)
    after={str(p.relative_to(ROOT)):pin(p)for p in tracked};require(before==after,'read inputs changed during extraction')
    result={'status':'four_pinned_mesh_offline_mapping_verified','engine_invoked':False,'world_modified':False,
            'targets':list(TARGETS),'source_pins':before,'sources_unchanged':True,'meshes':records,'artifacts':artifacts,
            'method_scope':'Existing reviewed HEADER and numeric helpers plus narrow exact observed one-surface literal extraction, existing compressed surface_positions formula. Not a general TSCN parser; RSRC parser does not apply to these text blocks.',
            'limits':['Native surface storage var_to_bytes hash is quoted from pinned intake, not independently recomputed.',
                      'Normals/tangents are preserved as exact storage bytes, not semantically decoded or regenerated.',
                      'No original UV/UV2 data exists on these four surfaces; adding UV is a new authored attribute.',
                      'Exact source RGBA8 and corner/index association are available; no Blender color-space/storage roundtrip has been tested.',
                      'No shadow/LOD/collision decoding, resource mutation, native creation, export, integration or acceptance is included.']}
    if write:(HERE/'mapping-summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=build(a.write)
    print(json.dumps({'status':r['status'],'sources_unchanged':r['sources_unchanged'],'meshes':[{k:m[k]for k in ['tile','vertex_count','index_count','unique_local_xyz_count','survey_ordered_float32_match','float32_max_component_error_m','survey_json_decimal_vs_float32_max_error_m','float32_translation_max_roundoff_m']}for m in r['meshes']]},indent=2))
