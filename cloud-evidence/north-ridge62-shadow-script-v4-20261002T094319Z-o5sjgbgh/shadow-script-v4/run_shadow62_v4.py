#!/usr/bin/env python3
"""Source checks by default; --collect is one separately scheduled CPU2/60s read."""
from __future__ import annotations
import argparse,ast,inspect,json,os,re,shutil,signal,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;V1=HERE.parent;V2=V1/'version-guard-v2';V3=V1/'shadow-arrays-v3'
sys.path[:0]=[str(HERE),str(V3),str(V2),str(V1)]
import run_shadow62_v3 as v3
previous=v3.previous;old=v3.old;legacy=v3.legacy;replay=v3.replay;validate_native=v3.validate_native;require=old.require
SCRIPT=HERE/'read_proxy_meshes62_v4.gd';AUDIT_SHA=v3.AUDIT_SHA
FROZEN_NAMES={'run_shadow62_v4.py','test_script_path62.py','read_proxy_meshes62_v4.gd','visible_geometry61.gd','native-request-v3.json','provenance.json','README.md','INDEPENDENT_REVIEW.md','TESTS.log','TESTS-optimized.log'}
OLD_BLOCK='\tif not check(FileAccess.get_sha256(ShadowAudit.resource_path) == AUDIT_SHA,"existing shadow audit source changed"): return empty\n\tvar auditor: Variant = ShadowAudit.new()\n'
NEW_BLOCK='\tvar auditor: Variant = ShadowAudit.new()\n\tvar audit_script_value: Variant = auditor.get_script()\n\tif not check(audit_script_value is Script,"existing shadow audit is not a Script"): return empty\n\tvar audit_script: Script = audit_script_value as Script\n\tif not check(FileAccess.get_sha256(audit_script.resource_path) == AUDIT_SHA,"existing shadow audit source changed"): return empty\n'
MAIN_SUBSTITUTIONS=[('shadow_arrays_v3_source_preparation_verified','shadow_script_v4_source_preparation_verified'),('north-ridge62-shadow-arrays-v3-','north-ridge62-shadow-script-v4-')]

def freeze_check():
    f=json.loads((HERE/'FINAL_SHA256.json').read_text());require(type(f)is dict and set(f)==FROZEN_NAMES,'v4 exact freeze set changed')
    for name,sha in f.items():require(type(sha)is str and re.fullmatch('[0-9a-f]{64}',sha)and old.digest(HERE/name)==sha,'v4 frozen source changed '+name)
    return f

def exact_collector(source):
    baseline=v3.SCRIPT.read_text();require(baseline.count(OLD_BLOCK)==1,'v3 failing access block changed')
    require(source==baseline.replace(OLD_BLOCK,NEW_BLOCK),'v4 collector changed outside typed Script access block')

def exact_main(source):
    baseline=inspect.getsource(v3.main)
    for a,b in MAIN_SUBSTITUTIONS:
        require(baseline.count(a)==1,'v3 main label changed');baseline=baseline.replace(a,b)
    require(source==baseline,'v4 launcher changed outside output/status labels')

def source_guards():
    v3.source_guards()
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    exact_collector(SCRIPT.read_text());exact_main(inspect.getsource(main))
    require(old.digest(HERE/'visible_geometry61.gd')==AUDIT_SHA,'v4 helper identity changed')
    require((HERE/'native-request-v3.json').read_bytes()==(V3/'native-request-v3.json').read_bytes(),'v4 protocol request changed')
    require(replay is v3.replay and validate_native is v3.validate_native,'v3 replay or schema replaced')

def provenance_check():
    p=json.loads((HERE/'provenance.json').read_text());pins=p['immutable_prior_files']
    for rel,pin in pins.items():
        path=legacy.AETHER/rel;require(path.is_file()and path.stat().st_size==pin['bytes']and old.digest(path)==pin['sha256'],'v4 prior input changed '+rel)
    prior=json.loads((legacy.AETHER/p['v3_failure_wrapper']).read_text())
    require(prior['passed']is False and prior['native_parse_passed']is False and prior['process']['returncode']==1 and prior['changed_inputs']==[],'v3 failure terminal changed')
    require(len(prior['log_errors'])==2 and 'Cannot find member "resource_path"'in prior['log_errors'][0],'v3 exact parser failure changed')
    bound={str(legacy.AETHER/rel):pin['sha256']for rel,pin in pins.items()}
    for rel,sha in v3.freeze_check().items():bound[str(V3/rel)]=sha
    return bound

def static():
    freeze_check();source_guards();pins=provenance_check()
    prep,req,inputs,priorpins=v3.static();pins.update(priorpins)
    return prep,req,inputs,pins

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',action='store_true');args=ap.parse_args();prep,request,inputs,pins=static()
    if not args.collect:
        print(json.dumps({'status':'shadow_script_v4_source_preparation_verified','saved_groups':775,'saved_instances':57797,'visual_query':676,'visual_design':575,'existing_shadow_helper_sha256':AUDIT_SHA,
                          'original_v1_v2_and_failure_unchanged':True,'indexed_and_actual_get_faces_bounds_separate':True,'no_epsilon_added':True,'engines_started':0,'native_parse_passed':False,'native_mesh_read_passed':False,'all_occupancy_complete':False},indent=2));return 0
    before=legacy.manifest();before.update(inputs);before.update(pins)
    for folder,reader in [(V1,old.freeze_check),(V2,previous.freeze_check),(HERE,freeze_check)]:
        for rel,sha in reader().items():before[str(folder/rel)]=sha
        before[str(folder/'FINAL_SHA256.json')]=old.digest(folder/'FINAL_SHA256.json')
    out=Path(tempfile.mkdtemp(prefix='north-ridge62-shadow-script-v4-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=legacy.AETHER/'cloud-evidence'));print(out,flush=True)
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
