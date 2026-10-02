#!/usr/bin/env python3
"""Source verification by default. --collect performs one later 60s/CPU2 saved read."""
from __future__ import annotations
import argparse,ast,gzip,hashlib,inspect,json,os,re,shutil,signal,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;V1=HERE.parent;V2=V1/'version-guard-v2'
sys.path[:0]=[str(HERE),str(V2),str(V1)]
import run_proxy62_v2 as previous
import prepare_proxy62 as original
import analyze_shadow62 as replay
from schema_shadow62 import request_v3,validate_native
legacy=previous.legacy;old=previous.old;require=old.require
SCRIPT=HERE/'read_proxy_meshes62_v3.gd'
AUDIT_SOURCE=legacy.AETHER/'source-assets/coast61-nearbay-orbit/visible_geometry61.gd'
AUDIT_SHA='966c863a02d136aefacb78e76d7301649b96c628408c589d3a4345fac30086f7'
FROZEN_NAMES={'schema_shadow62.py','test_shadow62.py','analyze_shadow62.py','run_shadow62_v3.py','read_proxy_meshes62_v3.gd','visible_geometry61.gd','native-request-v3.json','provenance.json','README.md','INDEPENDENT_REVIEW.md','TESTS.log','TESTS-optimized.log'}
ADAPTER_SUBSTITUTIONS=[('request=native_request(n,c)','request=request_v3(request_v2(native_request(n,c)))'),("x['combined_vertex_bounds']for x in native['visual_meshes']","x['combined_clearance_bounds']for x in native['visual_meshes']"),('source_specific_vertex_world_bounds','source_specific_visual_and_get_faces_world_bounds')]

def freeze_check():
    f=json.loads((HERE/'FINAL_SHA256.json').read_text());require(type(f)is dict and set(f)==FROZEN_NAMES,'v3 exact freeze set changed')
    for name,sha in f.items():require(type(sha)is str and re.fullmatch('[0-9a-f]{64}',sha)and old.digest(HERE/name)==sha,'v3 frozen source changed '+name)
    return f

def source_guards():
    previous.source_guards()
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    require(old.digest(AUDIT_SOURCE)==old.digest(HERE/'visible_geometry61.gd')==AUDIT_SHA,'existing strict shadow helper is not byte-identical')
    expected=inspect.getsource(original.analyze)
    for a,b in ADAPTER_SUBSTITUTIONS:
        require(expected.count(a)==1,'unexpected original adapter site');expected=expected.replace(a,b)
    require(inspect.getsource(replay.analyze)==expected,'all-group replay changed beyond three reviewed substitutions')
    code='\n'.join(x for x in SCRIPT.read_text().splitlines()if not x.lstrip().startswith('#'))
    require(code.startswith('extends "../version-guard-v2/read_proxy_meshes62_v2.gd"'),'v3 inheritance changed')
    require(re.findall(r'^func (\w+)\(',code,re.M)==['oriented_sha','empty_mesh_summary','read_one_mesh','mesh_summary','finish'],'v3 modified unrelated native methods')
    require('func _initialize'not in code and 'get_version_info'not in code,'v2 initialization/engine gate must stay inherited')
    original_finish=old.SCRIPT.read_text().split('func finish() -> void:',1)[1]
    expected_finish=original_finish.replace('JSON.stringify(result,"\\t")','JSON.stringify(result,"\\t",true,true)')
    require(SCRIPT.read_text().split('func finish() -> void:',1)[1]==expected_finish,'terminal writer changed beyond full-precision JSON serialization')
    allowed={'oriented_triangles','audit_surface','surface_positions','audit_array_mesh'}
    calls=set(re.findall(r'auditor\.(\w+)\(',code));require(calls==allowed,'unexpected helper entry point')
    require('const ShadowAudit = preload("visible_geometry61.gd")'in code,'unknown shadow helper')
    require('if not shadow_only:'in code and code.count('mesh.get_faces()')==1,'get_faces must be primary-only')
    for token in ['.snapped(step)','actual_sha == predicted_sha','"actual_indexed_base_faces"','"combined_clearance_bounds"','item.shadow_coverage_proof =','"get_faces_snap_proof"']:
        require(token in code,'missing exact v3 distinction/proof '+token)
    for pattern in [r'\.instantiate\s*\(',r'\.add_child\s*\(',r'PhysicsServer',r'ResourceSaver',r'\.buffer\b',r'\.set_faces\s*\(',r'\.prepare\s*\(']:
        require(re.search(pattern,code)is None,'forbidden v3 action '+pattern)

def provenance_check():
    p=json.loads((HERE/'provenance.json').read_text());pins=p['immutable_prior_files']
    for rel,pin in pins.items():
        path=legacy.AETHER/rel;require(path.is_file()and path.stat().st_size==pin['bytes']and old.digest(path)==pin['sha256'],'v3 prior input changed '+rel)
    prior=json.loads((legacy.AETHER/p['v2_failure_report']).read_text());require(prior['engine_version_guard']['passed']is True and prior['issues']==['native arrays unavailable']and len(prior['visual_meshes'])==1,'original v2 failure changed')
    diagnostic=json.loads((legacy.AETHER/p['exact_diagnosis']).read_text());require(diagnostic['native_primary_vertex_hash_exact']is True and diagnostic['native_get_faces_full_byte_hash_exact']is True and diagnostic['engines_started']==0,'diagnostic proof missing')
    require(diagnostic['native_report_sha256']==pins[p['v2_failure_report']]['sha256'],'diagnostic binding mismatch')
    return {str(legacy.AETHER/rel):pin['sha256']for rel,pin in pins.items()}

def static():
    freeze_check();source_guards();pins=provenance_check()
    prep,base,v2req,inputs,priorpins=previous.static();pins.update(priorpins)
    req=request_v3(v2req);require((HERE/'native-request-v3.json').read_bytes()==old.encode(req),'v3 request is not exact derivative')
    require(replay.validate_native is validate_native,'wrong replay geometry validator')
    return prep,req,inputs,pins

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',action='store_true');args=ap.parse_args();prep,request,inputs,pins=static()
    if not args.collect:
        print(json.dumps({'status':'shadow_arrays_v3_source_preparation_verified','saved_groups':775,'saved_instances':57797,'visual_query':676,'visual_design':575,'existing_shadow_helper_sha256':AUDIT_SHA,
                          'original_v1_v2_and_failure_unchanged':True,'indexed_and_actual_get_faces_bounds_separate':True,'no_epsilon_added':True,'engines_started':0,'native_parse_passed':False,'native_mesh_read_passed':False,'all_occupancy_complete':False},indent=2));return 0
    before=legacy.manifest();before.update(inputs);before.update(pins)
    for folder,reader in [(V1,old.freeze_check),(V2,previous.freeze_check),(HERE,freeze_check)]:
        for rel,sha in reader().items():before[str(folder/rel)]=sha
        before[str(folder/'FINAL_SHA256.json')]=old.digest(folder/'FINAL_SHA256.json')
    out=Path(tempfile.mkdtemp(prefix='north-ridge62-shadow-arrays-v3-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=legacy.AETHER/'cloud-evidence'));print(out,flush=True)
    result={'status':'preparing','passed':False,'native_mesh_read_passed':False,'native_parse_passed':False,'all_occupancy_complete':False,'runtime_collision_observed':False,'output':str(out)}
    def cancel(sig,frame):raise InterruptedError('wrapper signal '+str(sig))
    handlers={s:signal.signal(s,cancel)for s in [signal.SIGINT,signal.SIGTERM]}
    try:
        legacy.write_json(out/'wrapper-report.json',result);legacy.write_json(out/'input-sha256.json',before)
        for folder,dest in [(V1,out),(V2,out/V2.name),(HERE,out/HERE.name)]:
            dest.mkdir(exist_ok=True)
            for p in folder.glob('*.py'):shutil.copy2(p,dest/p.name)
        launches={old.SCRIPT:out/old.SCRIPT.name,previous.SCRIPT:out/V2.name/previous.SCRIPT.name,SCRIPT:out/HERE.name/SCRIPT.name,HERE/'visible_geometry61.gd':out/HERE.name/'visible_geometry61.gd',HERE/'native-request-v3.json':out/'native-request-v3.json'}
        for src,dest in launches.items():shutil.copy2(src,dest)
        copies={str(dest):before[str(src)]for src,dest in launches.items()};require(all(old.digest(path)==sha for path,sha in copies.items()),'copied launch input changed');before.update(copies)
        result['copied_native_launch_inputs']=copies;legacy.write_json(out/'input-sha256.json',before)
        userdata=out/'xdg';env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PROXY62_REQUEST=str(out/'native-request-v3.json'),PROXY62_OUTPUT=str(out/'native-proxy-meshes.json'))
        for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
            (userdata/name).mkdir(parents=True);env[key]=str(userdata/name)
        _,result['dependency_guard_before']=old.validate_dependencies();require(all(Path(p).is_file()and old.digest(p)==sha for p,sha in before.items()),'input changed before v3 native launch')
        command=[str(legacy.GODOT),'--headless','--path',str(legacy.PROJECT),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--script',str(out/HERE.name/SCRIPT.name)]
        result['status']='running';process=legacy.launch(command,out,env);result['process']=process
        logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace');errors=[l for l in logs.splitlines()if any(t in l for t in ['ERROR:','SCRIPT ERROR:','Parse Error:','Leaked instance','ObjectDB instances leaked'])];result['log_errors']=errors
        report=out/'native-proxy-meshes.json';native=json.loads(report.read_text());result['native_report_sha256']=old.digest(report)
        result['engine_version_info']=native.get('engine_version_info');result['engine_version_guard']=previous.validate_engine_observation(native,False)
        require(old.process_ok(process,errors),'native process failed');require(logs.count('NORTH62_PROXY_MESH_READ_END true')==1,'native completion marker missing')
        require(native['request_sha256']==old.digest(out/'native-request-v3.json'),'native request identity changed');validate_native(native,request)
        completed,actual_request,actual_inputs=replay.analyze(native);require(actual_request==request and actual_inputs==inputs,'native/source replay input mismatch')
        target=out/'source-specific-keep-reconcile.json';target.write_bytes(old.encode(completed))
        result.update(status='finished',passed=True,native_mesh_read_passed=True,native_parse_passed=True,keep_reconcile_sha256=old.digest(target),query_count=completed['combined_query_count'],design_count=completed['combined_design_count'],proxy_only_query_count=completed['proxy_only_query_count'])
    except BaseException as e:result.update(status='wrapper_exception',passed=False,exception=repr(e),native_mesh_read_passed=False)
    finally:
        try:
            _,result['dependency_guard_after']=old.validate_dependencies();require(result.get('dependency_guard_before')==result['dependency_guard_after'],'dependency summary changed')
        except BaseException as e:result.update(dependency_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        try:
            result['changed_inputs']=[p for p,sha in before.items()if not Path(p).is_file()or old.digest(p)!=sha]
            if result['changed_inputs']:result.update(passed=False,native_mesh_read_passed=False)
        except BaseException as e:result.update(identity_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        legacy.write_json(out/'wrapper-report.json',result)
        for s,h in handlers.items():signal.signal(s,h)
    print(json.dumps(result,indent=2));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
