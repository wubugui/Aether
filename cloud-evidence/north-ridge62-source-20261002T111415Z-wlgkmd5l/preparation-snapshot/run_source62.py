#!/usr/bin/env python3
"""Default is read-only preflight. Parent admits source and four-view stages separately."""
import argparse,os,sys,json,time,signal,tempfile,shutil,traceback,resource,struct
from pathlib import Path
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
sys.path.insert(0,str(Path(__file__).resolve().parent))
import contract62 as c
# Reuse the audited lifecycle/manifest helpers, without rewriting their framework.
sys.path.insert(0,str(c.ROOT/'source-assets/cloud-bank58/revision-k/import-v1'))
import bounded_support58k as support
import run_import58k as inherited
TOTAL={'source':60,'views':90}
MUTABLE={'north-ridge62.blend','source-attempt.json','source-terminal.json','views-attempt.json','views-terminal.json'}

def protected_manifest():
    paths={}
    for root in [c.ROOT/'source-assets',c.ROOT/'blender',c.ROOT/'assets',c.ROOT/'ref',inherited.PROJECT]:paths.update(inherited.file_manifest(root))
    paths[str(c.ROOT/'project.godot')]=c.sha(c.ROOT/'project.godot')
    for name in MUTABLE:paths.pop(str(c.HERE/name),None)
    return paths

def frozen_inputs():
    freeze=c.HERE/'FINAL_SHA256.json';data=c.read(freeze)
    paths={str(c.ROOT/path):row['sha256']for path,row in data['files'].items()};paths[str(freeze)]=c.sha(freeze)
    _,changed,errors=support.inspect_inputs(paths);c.require(not changed and not errors,'Frozen preparation identity '+repr(changed+errors));return paths

def png_info(path):
    data=path.read_bytes();c.require(data[:8]==b'\x89PNG\r\n\x1a\n' and data[12:16]==b'IHDR','Actual PNG')
    width,height=struct.unpack('>II',data[16:24]);c.require((width,height)==(1179,664),'No downscale / original fixed image size')
    return dict(bytes=len(data),sha256=c.sha(path),width=width,height=height)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-approved',choices=['source','views']);args=ap.parse_args()
    if not args.run_approved:
        c.check_binding(c.read(c.HERE/'bindings62.json'));frozen_inputs();print('Prepared only; no Blender, Godot, source or images created. Parent schedules each explicit stage.');return 0
    stage=args.run_approved;limit=TOTAL[stage]
    c.require(not (c.HERE/(stage+'-terminal.json')).exists(),'One-shot stage already retained')
    if stage=='source':c.require(not c.SOURCE.exists(),'Do not overwrite a source')
    else:
        prior=c.read(c.HERE/'source-terminal.json');c.require(prior['passed'] and prior['source_sha256']==c.sha(c.SOURCE),'Prior actual build/fresh-reopen passed and source unchanged')
    with (c.HERE/(stage+'-attempt.json')).open('x') as f:json.dump(dict(state='admitted_not_complete',pid=os.getpid(),stage=stage,utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())),f);f.flush();os.fsync(f.fileno())
    started=time.monotonic();run=Path(tempfile.mkdtemp(prefix='north-ridge62-'+stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=c.ROOT/'cloud-evidence'));print(run,flush=True)
    report=dict(version=c.VERSION,stage=stage,state='preparing',passed=False,run=str(run),limits=dict(total_wall_seconds=limit,cpu_threads=2,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB),stages=[],images=[],godot_started=False,world_loaded=False,world_modified=False,support_pending_rows=167,world_integration_allowed=False,visual_acceptance=False)
    before={};pins={};old_handlers={};outputs={};source_sha=c.sha(c.SOURCE) if stage=='views' else None
    def stop(number,frame):raise InterruptedError('Wrapper stop signal '+str(number))
    try:
        for sig in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):old_handlers[sig]=signal.signal(sig,stop)
        signal.setitimer(signal.ITIMER_REAL,limit)
        cpus=sorted(os.sched_getaffinity(0))[:2];c.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
        pins=frozen_inputs();c.require(c.sha(c.BLENDER)==c.BLENDER_SHA,'Official Blender executable pin')
        before=protected_manifest();support.atomic_json(run/'protected-before.json',before);support.atomic_json(run/'input-sha256.json',pins)
        # Snapshot only source instructions/data, never prior native output.
        snap=run/'preparation-snapshot';snap.mkdir()
        for path in c.HERE.iterdir():
            if path.is_file() and path.name not in MUTABLE:shutil.copy2(path,snap/path.name)
        output=run/'outputs';output.mkdir();env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
        env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('BLENDER_USER_CONFIG','blender-config')]:path=run/name;path.mkdir();env[key]=str(path)
        jobs=[('build',None),('verify',None)] if stage=='source' else [('render',v)for v in ['1131','1347','side','back']]
        raw_build=None;binding=c.read(c.HERE/'bindings62.json')
        for mode,view in jobs:
            c.require(frozen_inputs()==pins,'Frozen source preparation changed between processes')
            if source_sha:c.require(c.sha(c.SOURCE)==source_sha,'Saved source changed between processes')
            c.require(all(c.sha(path)==digest for path,digest in outputs.items()),'Earlier evidence changed')
            remaining=limit-(time.monotonic()-started)-8;c.require(remaining>0,'Total stage budget exhausted')
            label=mode+('-'+view if view else '')
            command=[str(c.BLENDER),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1','--python',str(c.HERE/'native62.py'),'--','--mode',mode,'--out',str(output)]
            if view:command+=['--view',view]
            report['state']='running';support.atomic_json(run/'wrapper-report.json',report)
            row=support.run_child(command,run,env,run,remaining,label);report['stages'].append(row);support.atomic_json(run/'wrapper-report.json',report)
            c.require(support.process_passed(row),'Native child failed '+label)
            c.require(not support.error_lines([run/(label+'.stdout.log'),run/(label+'.stderr.log')]),'Native error/leak log')
            terminal=c.read(output/(label+'-result.json'));rawpath=output/(label+'-raw.json');raw=c.read(rawpath)
            c.require(terminal['passed'] and terminal['state']=='completed' and terminal['version']==c.VERSION and terminal['mode']==mode and terminal['pid']==row['pid']==raw['pid'],'Native terminal/PID completion')
            c.require(terminal['raw_sha256']==c.sha(rawpath),'Raw saved before validation SHA binding')
            c.require(raw['cpu_affinity']==row['cpu_affinity']==cpus,'Actual CPU2 identity')
            c.require(terminal['validation']==c.validate_raw(raw,binding),'Wrapper independent raw validation')
            c.require(not terminal['world_loaded'] and not terminal['world_integration_allowed'] and not terminal['visual_acceptance'],'Source-only terminal scope')
            c.require(terminal['source_sha256']==c.sha(c.SOURCE),'Native saved source SHA')
            if mode=='build':c.require(terminal['source_saved'],'Native source save');raw_build={k:v for k,v in raw.items()if k not in ('pid','cpu_affinity')}
            elif mode=='verify':
                c.require(not terminal['source_saved'] and row['pid']!=report['stages'][0]['pid'],'Fresh independent process; no resave')
                c.require(raw_build=={k:v for k,v in raw.items()if k not in ('pid','cpu_affinity')},'Entire native source raw identity equal after fresh reopen')
            else:
                c.require(not terminal['source_saved'] and terminal['images']==1,'Exactly one no-save source view')
                info=png_info(output/('62-'+view+'.png'));c.require(info['sha256']==terminal['image_sha256'],'Actual image identity');report['images'].append(dict(view=view,**info))
            c.require(source_sha is None or c.sha(c.SOURCE)==source_sha,'Native no-save source bytes remained unchanged')
            if source_sha is None:source_sha=c.sha(c.SOURCE)
            outputs.update({p:c.sha(p)for p in output.iterdir()if p.is_file()})
        c.require(len(report['stages'])==len(jobs),'All required independent processes finished');report.update(passed=True,state='completed')
    except BaseException:report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        try:
            _,changed,errors=support.inspect_inputs(pins);after=protected_manifest();support.atomic_json(run/'protected-after.json',after)
            report.update(frozen_inputs_unchanged=bool(pins and not changed and not errors),changed_inputs=changed,input_errors=errors,protected_originals_unchanged=bool(before and before==after),protected_file_count=len(before),earlier_outputs_unchanged=all(c.sha(p)==digest for p,digest in outputs.items()))
            report['saved_source_unchanged']=bool(source_sha and c.SOURCE.exists() and c.sha(c.SOURCE)==source_sha)
            report['passed']=bool(report['passed'] and report['frozen_inputs_unchanged'] and report['protected_originals_unchanged'] and report['earlier_outputs_unchanged'] and report['saved_source_unchanged'])
        except BaseException:report.update(passed=False,finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in old_handlers.items():signal.signal(sig,handler)
        elapsed=time.monotonic()-started
        if elapsed>limit:report.update(passed=False,budget_overrun=True)
        report.update(state='completed' if report['passed'] else 'failed',total_wall_seconds=elapsed,actual_wrapper_peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256=c.sha(c.SOURCE)if c.SOURCE.exists()else None,source_bytes=c.SOURCE.stat().st_size if c.SOURCE.exists()else None,actual_wrapper_exit_code=0 if report['passed'] else 1)
        support.atomic_json(run/'wrapper-report.json',report);support.atomic_json(c.HERE/(stage+'-terminal.json'),report);(run/'exit-code.txt').write_text(str(report['actual_wrapper_exit_code'])+'\n')
    return report['actual_wrapper_exit_code']
if __name__=='__main__':raise SystemExit(main())
