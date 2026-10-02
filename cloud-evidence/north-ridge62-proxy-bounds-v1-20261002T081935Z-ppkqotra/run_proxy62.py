#!/usr/bin/env python3
"""Default source verification only. --collect runs exactly one 60s/CPU2 native read."""
import argparse,ast,hashlib,json,math,os,re,shutil,signal,sys,tempfile,time
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE),str(HERE.parent)]
import run_intake62 as legacy
from dependency_guard62 import validate_dependencies
from prepare_proxy62 import analyze,digest,encode,validate_native
SCRIPT=HERE/'read_proxy_meshes62.gd'

def require(ok,label):
    if not ok:raise RuntimeError(label)

FROZEN_NAMES={'proxy_math62.py','prepare_proxy62.py','run_proxy62.py','read_proxy_meshes62.gd','test_proxy62.py','README.md','INDEPENDENT_REVIEW.md','source-bounds-preparation.json','native-request.json','immutable-source-inputs.json','PREPARATION.json','TESTS.log','TESTS-optimized.log'}

def validate_freeze(freeze):
    require(type(freeze)is dict and set(freeze)==FROZEN_NAMES,'incomplete or unexpected freeze file set')
    require(all(type(v)is str and re.fullmatch('[0-9a-f]{64}',v)for v in freeze.values()),'invalid freeze hash')

def freeze_check():
    freeze=json.loads((HERE/'FINAL_SHA256.json').read_text());validate_freeze(freeze)
    for rel,sha in freeze.items():
        p=HERE/rel;require(p.is_file()and digest(p)==sha,'preparation freeze changed '+rel)
    return freeze

def source_guards():
    for path in HERE.glob('*.py'):ast.parse(path.read_text())
    code='\n'.join(line for line in SCRIPT.read_text().splitlines()if not line.lstrip().startswith('#'))
    for token in [r'\.instantiate\s*\(',r'\.add_child\s*\(',r'ResourceSaver',r'\.set_faces\s*\(',r'\.set_surface\w*\s*\(',r'get_instance_transform\s*\(',r'\.buffer\b',r'\.set_buffer\s*\(',r'get_viewport\s*\(',r'\.save\s*\(']:
        require(re.search(token,code)is None,'forbidden native source '+token)
    for token in ['surface_get_arrays','get_faces()','get_state()','get_node_instance(i)','get_node_count()','"runtime_collision_observed":false','"world_instantiated":false','"all_occupancy_complete":false','NORTH62_PROXY_MESH_READ_END']:
        require(token in code,'missing native evidence '+token)

def static():
    freeze_check();source_guards()
    result,request,inputs=analyze()
    require((HERE/'source-bounds-preparation.json').read_bytes()==encode(result),'prepared offline bounds differ')
    require((HERE/'native-request.json').read_bytes()==encode(request),'prepared mesh request differs')
    require((HERE/'immutable-source-inputs.json').read_bytes()==encode(inputs),'immutable source set differs')
    require(digest(legacy.GODOT)==legacy.ENGINE_SHA,'fixed 4.5.1 engine differs')
    return result,request,inputs

def process_ok(p,errors):
    return (p.get('status')=='finished'and p.get('returncode')==0 and p.get('exception')is None and p.get('external_signal')is None
            and p.get('timeout_triggered')is False and not errors and type(p.get('wall_seconds'))in(int,float)
            and math.isfinite(p['wall_seconds'])and 0<=p['wall_seconds']<=60 and len(p.get('cpu_affinity',[]))==2)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--collect',action='store_true');args=ap.parse_args()
    prep,request,inputs=static()
    if not args.collect:
        print(json.dumps({'status':'source_preparation_verified','saved_groups':775,'saved_instances':57797,'visual_query':676,'visual_design':575,
                          'combined_query_tree_only':prep['combined_query_count'],'proxy_only_query_tree_only':prep['proxy_only_query_count'],
                          'rock_native_read_pending':True,'engines_started':0,'native_parse_passed':False,'all_occupancy_complete':False,'immutable_inputs':len(inputs)},indent=2));return 0
    # Old evidence and all startup/remap controls, plus the entire new preparation, are frozen.
    before=legacy.manifest();before.update(inputs)
    for rel,sha in freeze_check().items():before[str(HERE/rel)]=sha
    before[str(HERE/'FINAL_SHA256.json')]=digest(HERE/'FINAL_SHA256.json')
    out=Path(tempfile.mkdtemp(prefix='north-ridge62-proxy-bounds-v1-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=legacy.AETHER/'cloud-evidence'));print(out,flush=True)
    result={'status':'preparing','passed':False,'native_mesh_read_passed':False,'native_parse_passed':False,'all_occupancy_complete':False,'runtime_collision_observed':False,'output':str(out)}
    def cancel(sig,frame):raise InterruptedError('wrapper signal '+str(sig))
    handlers={s:signal.signal(s,cancel)for s in [signal.SIGINT,signal.SIGTERM]}
    try:
        legacy.write_json(out/'wrapper-report.json',result);legacy.write_json(out/'input-sha256.json',before)
        shutil.copy2(SCRIPT,out/SCRIPT.name);shutil.copy2(HERE/'native-request.json',out/'native-request.json')
        # Snapshot only these small preparation scripts/request, never another full-world buffer.
        for p in HERE.glob('*.py'):shutil.copy2(p,out/p.name)
        userdata=out/'xdg';env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PROXY62_REQUEST=str(out/'native-request.json'),PROXY62_OUTPUT=str(out/'native-proxy-meshes.json'))
        for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
            (userdata/name).mkdir(parents=True);env[key]=str(userdata/name)
        _,result['dependency_guard_before']=validate_dependencies()
        require(all(Path(p).is_file()and digest(p)==sha for p,sha in before.items()),'input changed before native launch')
        command=[str(legacy.GODOT),'--headless','--path',str(legacy.PROJECT),'--audio-driver','Dummy','--rendering-method','gl_compatibility','--script',str(out/SCRIPT.name)]
        result['status']='running';process=legacy.launch(command,out,env);result['process']=process
        logs=(out/'stdout.log').read_text(errors='replace')+'\n'+(out/'stderr.log').read_text(errors='replace')
        errors=[l for l in logs.splitlines()if any(t in l for t in ['ERROR:','SCRIPT ERROR:','Parse Error:','Leaked instance','ObjectDB instances leaked'])];result['log_errors']=errors
        require(process_ok(process,errors),'native process failed')
        require(logs.count('NORTH62_PROXY_MESH_READ_END true')==1,'single successful native completion marker missing')
        p=out/'native-proxy-meshes.json';native=json.loads(p.read_text());require(native['request_sha256']==digest(out/'native-request.json'),'native request identity')
        validate_native(native,request)
        completed,actualrequest,actualinputs=analyze(native)
        require(actualrequest==request and actualinputs==inputs,'post-native source changed')
        (out/'source-specific-keep-reconcile.json').write_bytes(encode(completed))
        result.update(status='finished',passed=True,native_mesh_read_passed=True,native_parse_passed=True,native_report_sha256=digest(p),
                      keep_reconcile_sha256=digest(out/'source-specific-keep-reconcile.json'),query_count=completed['combined_query_count'],design_count=completed['combined_design_count'],proxy_only_query_count=completed['proxy_only_query_count'])
    except BaseException as e:result.update(status='wrapper_exception',passed=False,exception=repr(e),native_mesh_read_passed=False)
    finally:
        try:
            _,result['dependency_guard_after']=validate_dependencies()
            require(result.get('dependency_guard_before')==result['dependency_guard_after'],'dependency summary changed')
        except BaseException as e:result.update(dependency_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        try:
            result['changed_inputs']=[p for p,sha in before.items()if not Path(p).is_file()or digest(p)!=sha]
            if result['changed_inputs']:result.update(passed=False,native_mesh_read_passed=False)
        except BaseException as e:result.update(identity_recheck_error=repr(e),passed=False,native_mesh_read_passed=False)
        legacy.write_json(out/'wrapper-report.json',result)
        for s,h in handlers.items():signal.signal(s,h)
    print(json.dumps(result,indent=2));return 0 if result['passed']else 1
if __name__=='__main__':raise SystemExit(main())
