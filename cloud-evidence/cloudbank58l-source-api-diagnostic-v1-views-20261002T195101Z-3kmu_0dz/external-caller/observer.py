import ctypes, datetime, hashlib, importlib.util, json, os, pathlib, signal, subprocess, sys, tempfile, time, traceback
sys.dont_write_bytecode = True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
ROOT=pathlib.Path('/workspace/scratch/a29d03198654/Aether')
HERE=ROOT/'source-assets/cloud-bank58/revision-l/source-api-diagnostic-v1'
spec=importlib.util.spec_from_file_location('source_external_owned',HERE.parent/'source-runner-v3/deadline58l_v3.py')
D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def write(p,v):
    with pathlib.Path(p).open('x') as f: json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
if (HERE/'views-launch-observation.json').exists(): raise RuntimeError('External observation already exists; never repeat views')
libc=ctypes.CDLL(None,use_errno=True)
if libc.prctl(36,1,0,0,0)!=0: raise OSError(ctypes.get_errno(),'caller subreaper')
owned=D.Owned()
if set(owned.scan())!={os.getpid()}: raise RuntimeError('Caller has pre-existing children')
temp=pathlib.Path(tempfile.mkdtemp(prefix='aether-l-api-views-caller-',dir=ROOT.parent))
command=[sys.executable,'-B',str(HERE/'run58l_api_diagnostic.py'),'--run-approved','views']
rec=dict(stage='views',acceptance_mode='api_consistency_isolated_diagnostic_v1',full_native_acceptance=False,historical_default_corner_geometry_passed=False,command=command,cwd=str(ROOT),publication_commit='aa3c54c378eea644968bf0a95532f1300a6d3a51',process_exit_observed=False,actual_exit_code=None,timeout=False,cleanup=[],views_chain_verified=False,utc_started=datetime.datetime.now(datetime.timezone.utc).isoformat())
p=None;start=time.monotonic();rec['started_monotonic']=start
try:
    with (temp/'launcher.stdout.log').open('xb') as out,(temp/'launcher.stderr.log').open('xb') as err:
        p=subprocess.Popen(command,cwd=ROOT,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),stdout=out,stderr=err,start_new_session=True)
        rec['supervisor_pid']=p.pid;row=D.metadata(p.pid)
        if row is None or row['ppid']!=os.getpid(): raise RuntimeError('Actual launcher ownership unavailable')
        owned.pin(p.pid,'actual_external_Popen',row)
        print(json.dumps({'actual_views_launcher_pid':p.pid,'caller_directory':str(temp),'started_utc':rec['utc_started']}),flush=True)
        try: p.wait(timeout=max(.001,120-(time.monotonic()-start)))
        except subprocess.TimeoutExpired:
            rec['timeout']=True
            try: signal.pidfd_send_signal(owned.fds[p.pid],signal.SIGTERM)
            except ProcessLookupError: pass
            try: p.wait(timeout=1.1)
            except subprocess.TimeoutExpired: pass
    rec.update(actual_exit_code=p.returncode,process_exit_observed=p.returncode is not None,ended_monotonic=time.monotonic())
    rec['wall_seconds']=rec['ended_monotonic']-start
except BaseException:
    rec['caller_error']=traceback.format_exc();rec['wall_seconds']=time.monotonic()-start
finally:
    # Only explicitly owned descendants; failure cleanup never upgrades success.
    try:
        left=set(owned.scan())-{os.getpid()}
        if left:
            rec['orphan_or_live_owned_detected']=sorted(left);until=time.monotonic()+1.0
            while time.monotonic()<until:
                for pid in sorted(set(owned.scan())-{os.getpid()},reverse=True): owned.kill(pid,time.monotonic()-start)
                while True:
                    try: pid,status,usage=os.wait4(-1,os.WNOHANG)
                    except ChildProcessError: break
                    if not pid: break
                    code=os.waitstatus_to_exitcode(status);rec['cleanup'].append({'pid':pid,'returncode':code})
                    if p is not None and pid==p.pid: p.returncode=code
                if set(owned.scan())=={os.getpid()}: break
                time.sleep(.005)
        rec['remaining_owned_pids']=sorted(set(owned.scan())-{os.getpid()})
    except BaseException: rec['cleanup_error']=traceback.format_exc()
    rec['ownership_history']=owned.history;rec['cleanup_signals']=owned.kills;owned.close()
if p is not None and p.returncode is not None:
    rec['actual_exit_code']=p.returncode;rec['process_exit_observed']=True
rec['utc_process_observation_complete']=datetime.datetime.now(datetime.timezone.utc).isoformat()
run=None
terminal=HERE/'views-terminal.json'
if terminal.is_file():
    prior=json.loads(terminal.read_text());run=pathlib.Path(prior['run'])
    if run.resolve().parent!=(ROOT/'cloud-evidence').resolve(): raise RuntimeError('Unexpected evidence boundary')
    receipt=run/'supervisor-terminal.json'
    if receipt.is_file(): rec['supervisor_terminal_sha256']=sha(receipt)
rec.setdefault('supervisor_terminal_sha256',None)
write(HERE/'views-launch-observation.json',rec)
if rec['actual_exit_code']==0 and rec['process_exit_observed'] and not rec['timeout'] and not rec.get('caller_error') and not rec.get('orphan_or_live_owned_detected') and not rec.get('cleanup_error') and not rec.get('remaining_owned_pids') and 0<rec['wall_seconds']<120:
    try:
        sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent/'source-v1'))
        import run58l_api_diagnostic as runner, geometry58l as g
        runner.prior_source(g)  # Prior source bytes and actual source chain still valid.
        w=json.loads((HERE/'views-terminal.json').read_text());q=json.loads((run/'supervisor-terminal.json').read_text());ad=json.loads((HERE/'views-attempt.json').read_text())
        need=runner.native_support.require
        need(D.accepted(q) and q['diagnostic_acceptance'] is True and q['all_owned_children_reaped'] is True,'Actual successful reaped views supervisor')
        need(all(x['stage']=='views' and x['runner_version']==runner.VERSION and x['run']==str(run) and x['source']==str(g.SOURCE) and x['acceptance_mode']==runner.native_support.DIAGNOSTIC_MODE and x['full_native_acceptance'] is False for x in (ad,w,q)),'Exact views stage/identity/diagnostic scope')
        need(all(x['supervisor_pid']==rec['supervisor_pid'] for x in (ad,w,q)) and ad['wrapper_pid']==w['worker_pid']==q['worker_pid'],'Actual external launcher and native worker binding')
        need(q['admission_sha256']==w['admission_sha256']==sha(HERE/'views-attempt.json'),'Immutable actual views admission')
        need(q['terminal_sha256']==sha(HERE/'views-terminal.json') and q['wrapper_report_sha256']==sha(run/'wrapper-report.json') and (HERE/'views-terminal.json').read_bytes()==(run/'wrapper-report.json').read_bytes(),'Actual terminal/wrapper byte binding')
        need(w['passed'] is False and w['prepared_passed'] is True and w['diagnostic_prepared_passed'] is True and w['intended_worker_exit_code']==0,'Prepared only until actual external terminal')
        need(all(w[k] is True for k in ('frozen_inputs_unchanged','protected_originals_unchanged','earlier_outputs_unchanged','saved_source_unchanged')) and not w['changed_inputs'] and not w['input_errors'],'Actual complete protection')
        need(sha(g.SOURCE)=='7e72984235a84e63f5275f0287267656a8b11eaa651173856ae2beaa54ac5bd7' and g.SOURCE.stat().st_size==319519 and w['source_sha256']==q['source_sha256']==sha(g.SOURCE),'Exact published no-save source')
        binding=runner.support.strict_json(g.BINDING_PATH);views=[x['name'] for x in binding['world_cameras']];need(len(w['stages'])==len(w['images'])==len(views)==4,'Exactly four actual views')
        pids=[]
        for view,row,image_row in zip(views,w['stages'],w['images']):
            label='render-'+view;out=run/'outputs';native=json.loads((out/(label+'-result.json')).read_text())
            need(row==json.loads((run/(label+'.process.json')).read_text()) and runner.support.process_passed(row) and row['command']==runner.native_command(g,'render',out,HERE/'views-attempt.json',view),'Exact successful renderer command/process')
            need(native['pid']==row['pid'] and native['passed'] is True and native['state']=='completed' and native['mode']=='render' and native['view']==view and native['images']==1 and native['source_saved'] is False and native['exact_identity_restored'] is True,'Actual named completed no-save render')
            need(native['acceptance_mode']==runner.native_support.DIAGNOSTIC_MODE and native['full_native_acceptance'] is False and native['diagnostic_acceptance'] is True and native['source_sha256']==sha(g.SOURCE),'Actual diagnostic render scope')
            info=runner.png_info(out/(view+'.png'));need(image_row==dict(view=view,**info) and info['sha256']==native['image_sha256'],'Original decoded PNG bytes')
            for suffix,key in [('raw','raw_sha256'),('rendered-raw','rendered_raw_sha256'),('restored-raw','restored_raw_sha256')]:need(sha(out/(label+'-'+suffix+'.json'))==native[key],'Original actual render raw SHA')
            pids.append(row['pid'])
        need(len(set(pids))==4,'Independent actual four render PIDs')
        rec.update(views_chain_verified=True,source_sha256=sha(g.SOURCE),source_bytes=g.SOURCE.stat().st_size,run=str(run),views_render_stages=4,images=w['images'])
    except BaseException: rec['views_chain_error']=traceback.format_exc()
if run is None: run=pathlib.Path(tempfile.mkdtemp(prefix='cloudbank58l-source-api-diagnostic-v1-views-caller-failure-',dir=ROOT/'cloud-evidence'))
dest=run/'external-caller';temp.rename(dest)
pathlib.Path(__file__).rename(dest/'observer.py')
write(dest/'external-process-result.json',rec)
# Preserve the original factual observation and add the independent validation result.
write(HERE/'views-launch-validation.json',{'views_chain_verified':rec['views_chain_verified'],'external_result_sha256':sha(dest/'external-process-result.json'),'run':str(run)})
print(json.dumps({'run':str(run),'actual_exit_code':rec['actual_exit_code'],'wall_seconds':rec['wall_seconds'],'views_chain_verified':rec['views_chain_verified'],'source_bytes':rec.get('source_bytes'),'remaining_owned_pids':rec.get('remaining_owned_pids'),'error':rec.get('views_chain_error') or rec.get('caller_error')},ensure_ascii=False),flush=True)
raise SystemExit(0 if rec['views_chain_verified'] else 1)
