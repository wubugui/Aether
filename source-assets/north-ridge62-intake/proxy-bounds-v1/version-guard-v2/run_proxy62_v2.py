#!/usr/bin/env python3
"""Safe default: pure preparation checks. --collect is one later CPU2/60s native read."""
from __future__ import annotations
import argparse,ast,gzip,hashlib,json,os,re,shutil,signal,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
V1=HERE.parent
sys.path[:0]=[str(HERE),str(V1)]
import run_proxy62 as old
from version_schema62 import EXPECTED_ENGINE,POLICY,request_v2,engine_guard,validate_engine_observation,validate_native
legacy=old.legacy
SCRIPT=HERE/'read_proxy_meshes62_v2.gd'
BASELINE_FREEZE_SHA='95158efd63c46c8760f8df2c214524a2c5132c9a908a3ea69747c481d421e48f'
REFERENCE_RESULT_SHA='07384bbd9e1f74d48f67a1132a81e9f746db3c8182f9379aacbc69860542d8aa'
REFERENCE_WRAPPER_SHA='8e7783475d3291b10e1b1ac911739a27f026deb54de8475667af61ba72fa17b6'
FROZEN_NAMES={'version_schema62.py','run_proxy62_v2.py','read_proxy_meshes62_v2.gd','test_version_guard62.py',
              'native-request-v2.json','provenance.json','README.md','TESTS.log','TESTS-optimized.log','INDEPENDENT_REVIEW.md'}
require=old.require

def freeze_check():
    f=json.loads((HERE/'FINAL_SHA256.json').read_text())
    require(type(f)is dict and set(f)==FROZEN_NAMES,'v2 freeze file set changed')
    for name,sha in f.items():
        require(type(sha)is str and re.fullmatch('[0-9a-f]{64}',sha)and old.digest(HERE/name)==sha,'v2 frozen input changed '+name)
    return f

def source_guards():
    old.source_guards()
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    code='\n'.join(x for x in SCRIPT.read_text().splitlines()if not x.lstrip().startswith('#'))
    require(code.startswith('extends "../read_proxy_meshes62.gd"'),'v2 native inheritance changed')
    require(re.findall(r'^func (\w+)\(',code,re.M)==['engine_guard','_initialize'],'v2 must override only initialization plus version helper')
    require('begins_with'not in code and 'split('not in code,'version display-string matching is forbidden')
    match=re.search(r'^const EXPECTED_ENGINE: Dictionary = (\{.*\})$',code,re.M)
    require(match is not None and json.loads(match[1])==EXPECTED_ENGINE,'Python/GDScript exact engine constants differ')
    require('const ENGINE_POLICY: String = '+json.dumps(POLICY)in code,'version policy differs')
    observed=code.index('result.engine_version_info = observed.duplicate(true)')
    checked=code.index('result.engine_version_guard = engine_guard(observed)')
    visual=code.index('read_visual(want)')
    require(observed<checked<visual,'observation must precede version checks and mesh reads')
    require('"fixed_engine_version_mismatch"'in code and '"diagnostic":difference'in code,'missing native field diagnostics')
    require('typeof(actual) != typeof(wanted)'in code and 'actual != wanted'in code and 'not observed.has(field)'in code and 'not EXPECTED_ENGINE.has(field)'in code,'incomplete structured engine checks')
    for pattern in [r'\.instantiate\s*\(',r'\.add_child\s*\(',r'ResourceSaver',r'\.buffer\b',r'\.set_\w+\s*\(',r'\.save\s*\(']:
        require(re.search(pattern,code)is None,'forbidden v2 source action '+pattern)

def provenance_check():
    provenance=json.loads((HERE/'provenance.json').read_text());pins=provenance['immutable_prior_files']
    require(old.digest(V1/'FINAL_SHA256.json')==BASELINE_FREEZE_SHA,'original v1 freeze changed')
    for rel,pin in pins.items():
        path=legacy.AETHER/rel;require(path.is_file()and path.stat().st_size==pin['bytes']and old.digest(path)==pin['sha256'],'prior evidence changed '+rel)
    reference=json.loads((legacy.AETHER/provenance['reference_result']).read_text())
    wrapper=json.loads((legacy.AETHER/provenance['reference_wrapper']).read_text())
    require(pins[provenance['reference_result']]['sha256']==REFERENCE_RESULT_SHA and pins[provenance['reference_wrapper']]['sha256']==REFERENCE_WRAPPER_SHA,'fixed reference pin changed')
    require(reference['engine']==EXPECTED_ENGINE and reference['passed']is True,'reference native engine observation changed')
    require(wrapper['passed']is True and wrapper['native_result_sha256']==REFERENCE_RESULT_SHA and wrapper['godot_sha256']==legacy.ENGINE_SHA and not wrapper['changed_inputs']and not wrapper['logged_errors'],'reference engine binary binding failed')
    failure=json.loads((legacy.AETHER/provenance['first_failure_report']).read_text())
    require(failure['issues']==['fixed engine version']and failure['visual_meshes']==[]and failure['passed']is False and 'engine_version_info'not in failure,'original failure no longer exact')
    require(gzip.decompress((V1/'source-bounds-preparation.json.gz').read_bytes())==(V1/'source-bounds-preparation.json').read_bytes(),'parent gzip/raw identity')
    return {str(legacy.AETHER/rel):v['sha256']for rel,v in pins.items()}

def static():
    freeze_check();source_guards();pins=provenance_check()
    prep,request,inputs=old.static()
    new=request_v2(request)
    require((HERE/'native-request-v2.json').read_bytes()==old.encode(new),'v2 request is not the exact version-only derivative')
    require(engine_guard(EXPECTED_ENGINE)['passed'],'fixed observed fixture rejected')
    return prep,request,new,inputs,pins

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',action='store_true');args=ap.parse_args()
    prep,base_request,request,inputs,pins=static()
    if not args.collect:
        print(json.dumps({'status':'version_guard_v2_source_preparation_verified','expected_engine':EXPECTED_ENGINE,'fixed_engine_binary_sha256':legacy.ENGINE_SHA,
                          'original_freeze_sha256':BASELINE_FREEZE_SHA,'original_preparation_unchanged':True,'parent_gzip_raw_identical':True,
                          'saved_groups':775,'saved_instances':57797,'visual_query':676,'visual_design':575,'engines_started':0,
                          'v2_native_parse_passed':False,'native_mesh_read_passed':False,'all_occupancy_complete':False,'prior_pins':len(pins)},indent=2));return 0
    before=legacy.manifest();before.update(inputs);before.update(pins)
    for rel,sha in old.freeze_check().items():before[str(V1/rel)]=sha
    for rel,sha in freeze_check().items():before[str(HERE/rel)]=sha
    before[str(HERE/'FINAL_SHA256.json')]=old.digest(HERE/'FINAL_SHA256.json')
    before[str(V1/'FINAL_SHA256.json')]=BASELINE_FREEZE_SHA
    out=Path(tempfile.mkdtemp(prefix='north-ridge62-proxy-version-v2-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=legacy.AETHER/'cloud-evidence'));print(out,flush=True)
    result={'status':'preparing','passed':False,'native_mesh_read_passed':False,'native_parse_passed':False,'all_occupancy_complete':False,'runtime_collision_observed':False,'output':str(out)}
    def cancel(sig,frame):raise InterruptedError('wrapper signal '+str(sig))
    handlers={s:signal.signal(s,cancel)for s in [signal.SIGINT,signal.SIGTERM]}
    try:
        legacy.write_json(out/'wrapper-report.json',result);legacy.write_json(out/'input-sha256.json',before)
        (out/HERE.name).mkdir();shutil.copy2(SCRIPT,out/HERE.name/SCRIPT.name);shutil.copy2(old.SCRIPT,out/old.SCRIPT.name)
        shutil.copy2(HERE/'native-request-v2.json',out/'native-request-v2.json')
        for folder,dest in [(V1,out),(HERE,out/HERE.name)]:
            for p in folder.glob('*.py'):shutil.copy2(p,dest/p.name)
        userdata=out/'xdg';env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PROXY62_REQUEST=str(out/'native-request-v2.json'),PROXY62_OUTPUT=str(out/'native-proxy-meshes.json'))
        for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
            (userdata/name).mkdir(parents=True);env[key]=str(userdata/name)
        launch_copies={str(out/HERE.name/SCRIPT.name):before[str(SCRIPT)],str(out/old.SCRIPT.name):before[str(old.SCRIPT)],str(out/'native-request-v2.json'):before[str(HERE/'native-request-v2.json')]}
        require(all(old.digest(path)==sha for path,sha in launch_copies.items()),'copied native launch inputs differ')
        before.update(launch_copies);result['copied_native_launch_inputs']=launch_copies
        legacy.write_json(out/'input-sha256.json',before)
        _,result['dependency_guard_before']=old.validate_dependencies()
        require(all(Path(p).is_file()and old.digest(p)==sha for p,sha in before.items()),'input changed before v2 launch')
        command=[str(legacy.GODOT),'--headless','--path',str(legacy.PROJECT),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--script',str(out/HERE.name/SCRIPT.name)]
        result['status']='running';process=legacy.launch(command,out,env);result['process']=process
        logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
        errors=[l for l in logs.splitlines()if any(t in l for t in ['ERROR:','SCRIPT ERROR:','Parse Error:','Leaked instance','ObjectDB instances leaked'])];result['log_errors']=errors
        p=out/'native-proxy-meshes.json';native=json.loads(p.read_text());result['native_report_sha256']=old.digest(p)
        # Preserve structured diagnostics even when the child exits 2 at the version gate.
        result['engine_version_info']=native.get('engine_version_info');result['engine_version_guard']=validate_engine_observation(native,require_pass=False)
        require(old.process_ok(process,errors),'native process failed')
        require(logs.count('NORTH62_PROXY_MESH_READ_END true')==1,'single successful native completion marker missing')
        require(native['request_sha256']==old.digest(out/'native-request-v2.json'),'native request identity')
        validate_native(native,request)
        completed,actual_request,actual_inputs=old.analyze(native)
        require(actual_request==base_request and actual_inputs==inputs,'post-native v1 inputs changed')
        (out/'source-specific-keep-reconcile.json').write_bytes(old.encode(completed))
        result.update(status='finished',passed=True,native_mesh_read_passed=True,native_parse_passed=True,
                      keep_reconcile_sha256=old.digest(out/'source-specific-keep-reconcile.json'),query_count=completed['combined_query_count'],design_count=completed['combined_design_count'],proxy_only_query_count=completed['proxy_only_query_count'])
    except BaseException as e:result.update(status='wrapper_exception',passed=False,exception=repr(e),native_mesh_read_passed=False)
    finally:
        try:
            _,result['dependency_guard_after']=old.validate_dependencies()
            require(result.get('dependency_guard_before')==result['dependency_guard_after'],'dependency summary changed')
        except BaseException as e:result.update(dependency_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        try:
            result['changed_inputs']=[p for p,sha in before.items()if not Path(p).is_file()or old.digest(p)!=sha]
            if result['changed_inputs']:result.update(passed=False,native_mesh_read_passed=False)
        except BaseException as e:result.update(identity_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        legacy.write_json(out/'wrapper-report.json',result)
        for s,h in handlers.items():signal.signal(s,h)
    print(json.dumps(result,indent=2));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
