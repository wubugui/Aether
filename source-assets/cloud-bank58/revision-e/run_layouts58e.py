"""Scheduled two-source/four-image layout study; CPU2,90s,1.5GiB, no world."""
import argparse
from datetime import datetime,timezone
import json,os,resource,subprocess,sys,tempfile,time,traceback
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P.parent/'revision-d/native-01'))
import layouts58e as layouts
import common58d as c


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved-layout-study',action='store_true',required=True)
    parser.add_argument('--published-d-preview-commit',required=True);args=parser.parse_args()
    assert len(args.published_d_preview_commit)==40 and all(x in '0123456789abcdef' for x in args.published_d_preview_commit)
    blender=c.ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender';assert c.sha(blender)==c.BINARY_SHA256
    assert not any((P/(name+'.blend')).exists() for name in layouts.LAYOUTS)
    prepared=json.loads((P/'preparation-freeze58e.json').read_text())
    assert all(c.sha(c.ROOT/path)==r['sha256'] for path,r in prepared['files'].items())
    d_preview=P.parent/'revision-d/preview-01/preview-freeze58d-20261001T1634Z.json'
    committed=subprocess.run(['git','show',args.published_d_preview_commit+':'+str(d_preview.relative_to(c.ROOT))],cwd=c.ROOT,check=True,capture_output=True).stdout
    assert committed==d_preview.read_bytes(),'Declared published D preview differs'
    protected={}
    for manifest in [c.FREEZE,P.parent/'revision-d/native-01/native-freeze58d-20261001T1620Z.json',d_preview,P.parent/'revision-c-complete-freeze-20261001T1305Z.json']:
        protected.update(json.loads(manifest.read_text())['files'])
    assert all(c.sha(c.ROOT/path)==r['sha256'] for path,r in protected.items())
    png_helper=c.load_pure(P.parent/'revision-d/preview-01/run_preview58d.py')
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');run=Path(tempfile.mkdtemp(prefix='cloudbank58e-layouts-'+stamp+'-',dir=c.ROOT/'cloud-evidence'))
    for name in ['inputs','outputs','blender-config','xdg-cache','xdg-config','xdg-data']:(run/name).mkdir()
    state=dict(state='running',passed=False,complete=False,run_id=run.name,published_d_preview_commit=args.published_d_preview_commit,commands=[],images=[],single_shell=False,world_loaded=False,visual_acceptance=False)
    c.write(run/'process-report.json',state);c.write(run/'inputs/input-sha256.json',dict(files=prepared['files'],binary_sha256=c.sha(blender)))
    print(run,flush=True)
    env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
    jobs=[dict(script='build58e.py',args=[])]
    jobs += [dict(script='render_one58e.py',layout=name,view=view,args=['--layout',name,'--view',view]) for name in layouts.LAYOUTS for view in ['1216-source-front','shared-side-back']]
    start=time.monotonic();peak=0;reason=None;error=None;child=None
    try:
        for index,job in enumerate(jobs):
            if time.monotonic()-start>=90:reason='90 second total budget exhausted';break
            command=[str(blender),'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(P/job['script']),'--','--out',str(run/'outputs'),*job['args']]
            row=dict(job=job,state='running',complete=False,argv=command);state['commands'].append(row);c.write(run/'process-report.json',state)
            with (run/f'{index}-stdout.log').open('wb') as out,(run/f'{index}-stderr.log').open('wb') as err:
                child=subprocess.Popen(command,cwd=c.ROOT,env=env,stdout=out,stderr=err);row['pid']=child.pid
                while child.poll() is None:
                    current=None;elapsed=time.monotonic()-start
                    try:
                        line=next((s for s in (Path('/proc')/str(child.pid)/'status').read_text().splitlines() if s.startswith('VmRSS:')),None)
                        if line:current=int(line.split()[1]);peak=max(peak,current)
                    except FileNotFoundError:pass
                    c.write(run/'live-resource.json',dict(state='running',job=index,elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak))
                    if elapsed>90:reason='90 second total budget exceeded'
                    if peak>1572864:reason='1.5 GiB observed RSS exceeded'
                    if reason:
                        child.terminate()
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait()
                        break
                    time.sleep(.2)
                code=child.wait();child=None
            (run/f'{index}-child.exit-code').write_text(str(code)+'\n');row.update(state='completed',actual_child_exit_code=code,complete=code==0 and not reason)
            if resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss>1572864:reason='1.5 GiB actual child peak exceeded';row['complete']=False
            if index==0 and row['complete']:
                built=json.loads((run/'outputs/build-result58e.json').read_text());row['complete']=built['passed']
                if any(r['source_bytes']>1048576 for r in built['layouts']):reason='Source exceeds 1 MiB report threshold; preserve and stop';row['complete']=False
            if index>0 and row['complete']:
                base=job['layout']+'-'+job['view'];proof=json.loads((run/'outputs'/(base+'-proof.json')).read_text());image=run/'outputs'/(base+'.png');info=png_helper.png_info(image)
                expected=(836,471) if job['view']=='1216-source-front' else (836,586)
                row['complete']=proof['passed'] and info['sha256']==proof['image_sha256'] and (info['width'],info['height'])==expected
                state['images'].append(dict(layout=job['layout'],view=job['view'],**info))
            c.write(run/'process-report.json',state)
            if not row['complete']:break
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    finally:
        same=all(c.sha(c.ROOT/path)==r['sha256'] for path,r in protected.items())
        inputs_same=all(c.sha(c.ROOT/path)==r['sha256'] for path,r in prepared['files'].items())
        complete=bool(len(state['commands'])==5 and len(state['images'])==4 and all(r['complete'] for r in state['commands']) and same and inputs_same and not reason and not error)
        code=0 if complete else 1;state.update(state='completed',passed=complete,complete=complete,actual_wrapper_exit_code=code,error=error,limit_stop_reason=reason,
            elapsed_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,actual_peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,protected_unchanged=same,prepared_inputs_unchanged=inputs_same,
            source_files={name:dict(bytes=(P/(name+'.blend')).stat().st_size,sha256=c.sha(P/(name+'.blend'))) for name in layouts.LAYOUTS if (P/(name+'.blend')).exists()},final_shell_or_corridor_validation=False)
        c.write(run/'process-report.json',state);c.write(run/'terminal-proof.json',dict(process_report_sha256=c.sha(run/'process-report.json'),complete=complete));(run/'wrapper.exit-code').write_text(str(code)+'\n')
    print(json.dumps(state,indent=2),flush=True);return code


if __name__=='__main__':sys.exit(main())
