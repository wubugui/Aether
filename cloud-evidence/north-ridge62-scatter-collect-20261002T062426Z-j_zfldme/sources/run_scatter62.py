#!/usr/bin/env python3
"""Safe default: source checks only. Explicit coordinated --parse-only/--collect."""
from __future__ import annotations
import argparse,ast,gzip,hashlib,json,math,os,re,shutil,signal,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import run_intake62 as legacy
from dependency_guard62 import validate_dependencies
from build_inputs62 import build,encode,baseline
from scene_inputs62 import compose,f32

AETHER=HERE.parents[2]
SCRIPT=HERE/'collect_scatter62.gd'

def require(ok,message):
    if not ok:raise RuntimeError(message)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def raw_sha(raw):return hashlib.sha256(raw).hexdigest()
def prepared():
    packed=(HERE/'prepared-inputs.json.gz').read_bytes();info=json.loads((HERE/'prepared-inputs-identity.json').read_text());raw=gzip.decompress(packed)
    require(len(packed)==info['gzip_bytes']and raw_sha(packed)==info['gzip_sha256'],'prepared gzip identity mismatch')
    require(len(raw)==info['raw_bytes']and raw_sha(raw)==info['raw_sha256'],'prepared raw identity mismatch')
    require(raw==encode(build()),'prepared metadata no longer matches independent exact source decoding')
    return raw,json.loads(raw)

def sources():
    return sorted(p for p in HERE.rglob('*')if p.is_file()and '__pycache__'not in p.parts and p.name not in ['PREPARATION.json','TESTS.json','TESTS-optimized.json','FINAL_SHA256.json'])

def manifest():
    values=legacy.manifest()
    for p in sources():values[str(p)]=digest(p)
    return dict(sorted(values.items()))

def source_guards(code):
    filtered='\n'.join(x for x in code.splitlines()if not x.lstrip().startswith('#'))
    for pattern in [r'\.instantiate\s*\(',r'\.add_child\s*\(',r'ResourceSaver',r'get_instance_transform\s*\(',r'get_instance_color\s*\(',r'get_instance_custom_data\s*\(',r'\.set_instance_',r'\.set_buffer\s*\(',r'\.buffer\s*=',r'\.get_viewport\s*\(',r'\.get_aabb\s*\(']:
        candidate=filtered.replace('array_mesh.get_aabb()','')if 'get_aabb'in pattern else filtered
        require(not re.search(pattern,candidate),'forbidden source action '+pattern)
    for required in ['extends "collect_saved62.gd"','mm.buffer','buffer.to_byte_array()','node_transform * local','world * local_box','mm.instance_count*stride','"native_saved_buffer_hash_mismatch"','"native_mesh_binding_mismatch"','"independent_saved_transform_mismatch"','"exact775group_count_mismatch"','"all_occupancy_complete":false','"runtime_generated_entities_proved":false','"shader_deformation_envelopes_proved":false','save_scatter(false)','save_scatter(true)']:
        require(required in filtered,'missing source guard '+required)

def static():
    original=legacy.static_checks();raw,inputs=prepared()
    for p in HERE.glob('*.py'):ast.parse(p.read_text())
    source_guards(SCRIPT.read_text())
    upstream=json.loads((HERE/'upstream/source-manifest.json').read_text())
    require(len(upstream)==11,'expected11 official primary snapshots')
    for row in upstream:
        p=HERE/'upstream'/row['path'];require(p.stat().st_size==row['bytes']and digest(p)==row['sha256'],'upstream identity mismatch')
        require(row['source'].startswith('https://raw.githubusercontent.com/godotengine/godot/4.5.1-stable/'),'unpinned source')
    return {'status':'source_preparation_only','godot_invoked':False,'native_parse_passed':False,'native_collection_passed':False,'native_buffer_retention_verified':False,'all_occupancy_complete':False,'source_summary':inputs['source_summary'],'prepared_raw_sha256':raw_sha(raw),'prepared_raw_bytes':len(raw),'full_dependency_guard':original['dependency_guard'],'protected_input_count':len(manifest()),'official_source_count':len(upstream)}

def finite_vec(value,length=3):
    return isinstance(value,list) and len(value)==length and all(type(x) in (int,float) and math.isfinite(x) for x in value)

def transform_values(record):
    require(isinstance(record,dict),'missing transform record')
    columns=record.get('basis_columns');origin=record.get('origin')
    require(isinstance(columns,list) and len(columns)==3 and all(finite_vec(x) for x in columns) and finite_vec(origin),'invalid transform record')
    native=record.get('native_variant_hex')
    require(isinstance(native,str) and len(native)==104 and bytes.fromhex(native)[:4]==b'\x12\0\0\0','invalid transform native encoding')
    return [f32(v) for column in columns for v in column]+[f32(v)for v in origin]

def valid_bounds(value):
    return (isinstance(value,dict) and finite_vec(value.get('min')) and finite_vec(value.get('max'))
            and all(value['min'][i]<=value['max'][i]for i in range(3)))

def bound_hits(value,query):
    return value['max'][0]>=query[0] and value['min'][0]<=query[1] and value['max'][2]>=query[2] and value['min'][2]<=query[3]

def validate_output(value,inputs):
    require(value.get('status')=='complete'and value.get('issues')==[],'incomplete native output')
    require(value.get('expected_inputs_sha256')==raw_sha(encode(inputs)),'native expected-input identity missing/different')
    require(value.get('baseline_native_intake_sha256')==inputs['baseline_native_intake_sha256'],'native baseline identity missing/different')
    for key in ['design_box','query_box_with_40m']:
        require(value.get(key)==inputs[key],'native query identity missing/different')
    require(value.get('saved_data_read_complete')is True and value.get('saved_affine_bound_mesh_aabbs_complete')is True,'native saved data false')
    require(value.get('saved_group_count')==775 and len(value.get('groups',[]))==775,'native group count mismatch')
    expected={x['path']:x for x in inputs['groups']};actual={x['path']:x for x in value['groups']}
    require(len(actual)==775 and set(actual)==set(expected),'native group identities differ')
    require(value.get('saved_instance_count')==inputs['source_summary']['saved_instance_count'],'native total instance count mismatch')
    require(value.get('scene_sources')==inputs['scene_sources'],'native scene sources differ')
    require(valid_bounds(value.get('world_bounds_including_shadow')),'missing native global bounds')
    meshes=value.get('mesh_resources');require(isinstance(meshes,dict) and meshes,'missing mesh records')
    require(isinstance(value.get('material_resources'),dict),'missing material inventory')
    total_query=0;total_design=0
    for path,item in actual.items():
        want=expected[path];saved=want['saved_buffer']
        require(item.get('saved_data_complete')is True,'incomplete native group')
        require(item['resource']==want['resource']and item['saved_property_source']==want['saved_property_source'],'native binding changed')
        require(transform_values(item.get('world_transform'))==want['world_transform_columns'],'native node transform differs')
        for key in ['instance_count','stride_floats','buffer_float_count','buffer_sha256','mesh_resource','use_colors','use_custom_data','transform_format']:
            require(item[key]==saved[key],'native group saved input mismatch '+key)
        local_bounds=item.get('local_model_bounds_including_shadow');require(valid_bounds(local_bounds),'missing model bounds')
        require(item['mesh_resource']in meshes,'missing bound mesh inventory')
        mesh=meshes[item['mesh_resource']]
        require(valid_bounds(mesh.get('base_bounds')) and mesh.get('combined_bounds_including_shadow')==local_bounds,'bound mesh inventory differs')
        require(mesh.get('vertex_payload_bounds_independently_recomputed')is False and mesh.get('undeformed_saved_geometry_only')is True,'overclaimed mesh proof')
        require(item.get('saved_empty_group')==(item['instance_count']==0),'empty group classification differs')
        require(item.get('world_bounds_including_shadow')is None if item['instance_count']==0 else valid_bounds(item.get('world_bounds_including_shadow')),'missing group bounds')
        require(item.get('shader_deformation_envelope_proved')is False and item.get('runtime_model_scene_and_collision_proved')is False and bool(item.get('unsupported_reasons')),'missing group limitations')
        records=item['instances_overlapping_query'];require(len(records)==item['query_instance_count'],'query instance count mismatch')
        require(len({r['index']for r in records})==len(records),'duplicate hit index')
        require(all(type(r['index'])is int and 0<=r['index']<item['instance_count']for r in records),'hit index outside saved buffer')
        for hit in records:
            require(valid_bounds(hit.get('world_bounds_including_shadow')),'missing hit bounds')
            require(bound_hits(hit['world_bounds_including_shadow'],inputs['query_box_with_40m']),'exported non-query hit')
            require(hit.get('hits_design')==bound_hits(hit['world_bounds_including_shadow'],inputs['design_box']),'wrong design hit')
            local=transform_values(hit.get('local_transform'));world=transform_values(hit.get('world_transform'))
            require(compose(want['world_transform_columns'],local)==world and finite_vec(hit.get('world_origin')) and [f32(v)for v in hit['world_origin']]==world[9:],'wrong composed hit transform')
        require(sum(bool(r['hits_design'])for r in records)==item['design_instance_count'],'design count mismatch')
        total_query+=item['query_instance_count'];total_design+=item['design_instance_count']
    require(total_query==value['query_instance_count']and total_design==value['design_instance_count'],'native aggregate mismatch')
    for key in ['all_occupancy_complete','shader_deformation_envelopes_proved','runtime_generated_entities_proved','road_width_proved','visual_acceptance']:
        require(value.get(key)is False,'overclaimed evidence '+key)

def process_ok(process,errors):
    elapsed=process.get('wall_seconds')
    return (process.get('status')=='finished' and process.get('exception') is None
            and process.get('returncode')==0 and process.get('timeout_triggered') is False
            and process.get('external_signal') is None and not errors
            and type(elapsed) in (int,float) and math.isfinite(elapsed) and 0<=elapsed<=60)

def main():
    parser=argparse.ArgumentParser(description=__doc__);mode=parser.add_mutually_exclusive_group();mode.add_argument('--static-only',action='store_true');mode.add_argument('--parse-only',action='store_true');mode.add_argument('--collect',action='store_true');args=parser.parse_args()
    preparation=static()
    if not(args.parse_only or args.collect):print(json.dumps(preparation,indent=2));return 0
    before=manifest();raw,inputs=prepared();label='scatter-parse'if args.parse_only else 'scatter-collect'
    out=Path(tempfile.mkdtemp(prefix='north-ridge62-'+label+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=AETHER/'cloud-evidence'));print(out,flush=True)
    result={'status':'preparing','mode':label,'passed':False,'native_parse_passed':False,'native_collection_passed':False,'native_buffer_retention_verified':False,'all_occupancy_complete':False,'output':str(out)}
    def cancel(signum,_frame):
        result['wrapper_received_signal']=signum;raise InterruptedError('wrapper received signal '+str(signum))
    handlers={sig:signal.signal(sig,cancel)for sig in [signal.SIGINT,signal.SIGTERM]}
    try:
        legacy.write_json(out/'wrapper-report.json',result);legacy.write_json(out/'input-sha256.json',before);legacy.write_json(out/'preparation.json',preparation)
        (out/'prepared-inputs.json').write_bytes(raw)
        for p in sources():
            target=out/'sources'/p.relative_to(HERE);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        shutil.copy2(SCRIPT,out/SCRIPT.name);shutil.copy2(legacy.SCRIPT,out/legacy.SCRIPT.name)
        userdata=Path(tempfile.mkdtemp(prefix='scatter62-xdg-',dir=AETHER.parent/'tools-feiting'));env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',SCATTER62_INPUTS=str(out/'prepared-inputs.json'),SCATTER62_OUTPUT=str(out/'native-scatter.json'))
        for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
            (userdata/name).mkdir();env[key]=str(userdata/name)
        command=[str(legacy.GODOT),'--headless','--path',str(legacy.PROJECT),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--script',str(out/SCRIPT.name)]
        if args.parse_only:command.insert(1,'--check-only')
        _,result['dependency_guard_before']=validate_dependencies();require(before==manifest(),'input changed before launch')
        result['status']='running';process=legacy.launch(command,out,env);result['process']=process
        logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace');errors=[line for line in logs.splitlines()if any(t in line for t in ['ERROR:','SCRIPT ERROR:','Parse Error:','Leaked instance','ObjectDB instances leaked'])];result['log_errors']=errors
        ok=process_ok(process,errors)
        if args.parse_only:result['native_parse_passed']=bool(ok)
        else:
            path=out/'native-scatter.json';require(path.is_file(),'native output missing');native=json.loads(path.read_text());result['native_scatter_sha256']=digest(path);result['native_saved_group_count']=native.get('saved_group_count');result['native_status']=native.get('status')
            if ok:
                validate_output(native,inputs);require('NORTH62_SCATTER_END'in logs,'native completion marker missing')
                result.update(native_collection_passed=True,native_buffer_retention_verified=True,saved_instance_count=native['saved_instance_count'],query_instance_count=native['query_instance_count'],design_instance_count=native['design_instance_count'])
        result.update(status='finished',passed=bool(ok))
    except BaseException as exc:result.update(status='wrapper_exception',exception=repr(exc),passed=False,native_collection_passed=False,native_buffer_retention_verified=False)
    finally:
        try:_,result['dependency_guard_after']=validate_dependencies()
        except BaseException as exc:result.update(dependency_guard_recheck_error=repr(exc),passed=False,native_parse_passed=False,native_collection_passed=False,native_buffer_retention_verified=False)
        try:
            changed=[p for p,sha in before.items()if not Path(p).is_file()or digest(Path(p))!=sha];result['changed_inputs']=changed
            if changed:result.update(passed=False,native_parse_passed=False,native_collection_passed=False,native_buffer_retention_verified=False)
        except BaseException as exc:result.update(identity_recheck_error=repr(exc),passed=False,native_parse_passed=False,native_collection_passed=False,native_buffer_retention_verified=False)
        legacy.write_json(out/'wrapper-report.json',result)
        for sig,handler in handlers.items():signal.signal(sig,handler)
    print(json.dumps(result,indent=2));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
