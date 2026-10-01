"""Five fresh single-image processes, sequential, total 90s / CPU2 / 1.5GiB."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import resource
import struct
import subprocess
import sys
import tempfile
import time
import traceback
import zlib

P=Path(__file__).resolve().parent
N=P.parent/'native-01'
sys.path.insert(0,str(N))
import common58d as c

VIEWS=['1216-source-front','back','side','underside','top']
NATIVE_RUN=c.ROOT/'cloud-evidence/cloudbank58d-native-20261001T162033Z-y035f3f3'


def png_info(path):
    raw=path.read_bytes()
    assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    offset=8;data=[];header=None;ended=False
    while offset<len(raw):
        size=struct.unpack('>I',raw[offset:offset+4])[0]
        kind=raw[offset+4:offset+8];payload=raw[offset+8:offset+8+size]
        crc=struct.unpack('>I',raw[offset+8+size:offset+12+size])[0]
        assert zlib.crc32(kind+payload)&0xffffffff==crc,'PNG CRC mismatch'
        if kind==b'IHDR':header=struct.unpack('>IIBBBBB',payload)
        if kind==b'IDAT':data.append(payload)
        offset+=size+12
        if kind==b'IEND':ended=True;break
    assert ended and offset==len(raw) and header is not None
    width,height,depth,color,compression,filter_method,interlace=header
    assert depth==8 and color==2 and interlace==0
    decoded=zlib.decompress(b''.join(data))
    assert len(decoded)==height*(1+width*3)
    return dict(name=path.name,width=width,height=height,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                png_crc_complete=True,decoded_scanline_bytes=len(decoded))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-approved-five-view-preview',action='store_true',required=True)
    parser.add_argument('--published-native-commit',required=True,help='Exact remote commit verified by parent before launch')
    args=parser.parse_args()
    assert len(args.published_native_commit)==40 and all(ch in '0123456789abcdef' for ch in args.published_native_commit)
    blender=c.ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
    assert c.sha(blender)==c.BINARY_SHA256
    prepared=json.loads((P/'preview-input-freeze58d.json').read_text())
    assert all(c.sha(c.ROOT/path)==row['sha256'] for path,row in prepared['files'].items())
    # Parent owns remote verification. This independently binds its declared
    # published commit to the exact native bytes consumed locally.
    published_blob=subprocess.run(['git','show',args.published_native_commit+':'+str(c.SOURCE.relative_to(c.ROOT))],cwd=c.ROOT,check=True,capture_output=True).stdout
    assert hashlib.sha256(published_blob).hexdigest()==c.sha(c.SOURCE)
    protected={}
    for manifest in [c.FREEZE,N/'native-freeze58d-20261001T1620Z.json',c.BANK/'revision-c-complete-freeze-20261001T1305Z.json']:
        protected.update(json.loads(manifest.read_text())['files'])
    assert all(c.sha(c.ROOT/path)==row['sha256'] for path,row in protected.items())
    native=json.loads((NATIVE_RUN/'outputs/fresh-readback58d.json').read_text())
    assert native['passed'] and native['source_sha256']==c.sha(c.SOURCE)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run=Path(tempfile.mkdtemp(prefix='cloudbank58d-preview-'+stamp+'-',dir=c.ROOT/'cloud-evidence'))
    for name in ['inputs','images','blender-config','xdg-cache','xdg-config','xdg-data']:(run/name).mkdir()
    state=dict(state='running',complete=False,passed=False,run_id=run.name,published_native_commit=args.published_native_commit,
               expected_views=VIEWS,commands=[],images=[],world_loaded=False,visual_acceptance=False)
    c.write(run/'process-report.json',state)
    c.write(run/'inputs'/'input-sha256.json',dict(files=prepared['files'],preview_freeze_sha256=c.sha(P/'preview-input-freeze58d.json'),
            binary_sha256=c.sha(blender),source_sha256=c.sha(c.SOURCE),source_bytes=c.SOURCE.stat().st_size,
            published_commit_source_bytes_exact=True,published_native_commit=args.published_native_commit))
    print(run,flush=True)
    env=os.environ.copy()
    env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',
               BLENDER_USER_CONFIG=str(run/'blender-config'),XDG_CACHE_HOME=str(run/'xdg-cache'),
               XDG_CONFIG_HOME=str(run/'xdg-config'),XDG_DATA_HOME=str(run/'xdg-data'))
    start=time.monotonic();peak=0;reason=None;error=None;child=None
    try:
        for index,view in enumerate(VIEWS):
            if time.monotonic()-start>=90:
                reason='90 second total budget exhausted before next image';break
            command=[str(blender),'--factory-startup','-b','-t','2','--python-exit-code','1','--python',str(P/'render_one58d.py'),
                     '--','--view',view,'--out',str(run/'images')]
            row=dict(view=view,state='running',complete=False,argv=command)
            state['commands'].append(row);c.write(run/'process-report.json',state)
            with (run/f'{index}-{view}-stdout.log').open('wb') as out,(run/f'{index}-{view}-stderr.log').open('wb') as err:
                child=subprocess.Popen(command,cwd=c.ROOT,env=env,stdout=out,stderr=err)
                row['pid']=child.pid
                (run/f'{index}-child.pid').write_text(str(child.pid)+'\n')
                while child.poll() is None:
                    current=None;elapsed=time.monotonic()-start
                    try:
                        rss=next((line for line in (Path('/proc')/str(child.pid)/'status').read_text().splitlines() if line.startswith('VmRSS:')),None)
                        if rss:current=int(rss.split()[1]);peak=max(peak,current)
                    except FileNotFoundError:pass
                    c.write(run/'live-resource.json',dict(state='running',view=view,elapsed_seconds=elapsed,current_rss_kib=current,peak_observed_rss_kib=peak,completed_images=len(state['images'])))
                    if elapsed>90:reason='90 second total preview budget exceeded'
                    if peak>1572864:reason='1.5 GiB observed RSS exceeded'
                    if reason:
                        child.terminate()
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait()
                        break
                    time.sleep(.2)
                code=child.wait();child=None
            (run/f'{index}-child.exit-code').write_text(str(code)+'\n')
            actual_peak=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            if actual_peak>1572864:reason=reason or 'Actual child peak RSS exceeded 1.5 GiB'
            row.update(state='completed',actual_child_exit_code=code,complete=False)
            image=run/'images'/('cloudbank58d-'+view+'.png')
            proof=run/'images'/(view+'-image-proof.json')
            if code==0 and not reason and proof.exists() and image.exists():
                data=json.loads(proof.read_text());info=png_info(image)
                expected=(836,471) if view=='1216-source-front' else (836,586)
                row['complete']=bool(data['passed'] and info['sha256']==data['image_sha256'] and (info['width'],info['height'])==expected)
                state['images'].append(dict(view=view,**info))
            c.write(run/'process-report.json',state)
            if not row['complete']:break
    except BaseException:
        error=traceback.format_exc();(run/'wrapper-error.log').write_text(error)
        if child is not None and child.poll() is None:
            child.terminate()
            try:child.wait(timeout=3)
            except subprocess.TimeoutExpired:child.kill();child.wait()
    finally:
        protected_same=all(c.sha(c.ROOT/path)==row['sha256'] for path,row in protected.items())
        inputs_same=all(c.sha(c.ROOT/path)==row['sha256'] for path,row in prepared['files'].items())
        complete=bool(len(state['commands'])==5 and len(state['images'])==5 and all(row['complete'] for row in state['commands'])
                      and not reason and not error and protected_same and inputs_same)
        code=0 if complete else 1
        state.update(state='completed',complete=complete,passed=complete,actual_wrapper_exit_code=code,limit_stop_reason=reason,error=error,
                     elapsed_seconds=time.monotonic()-start,peak_observed_rss_kib=peak,actual_peak_child_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                     protected_inputs_unchanged=protected_same,preview_inputs_unchanged=inputs_same,source_sha256=c.sha(c.SOURCE),source_saved=False,
                     partial_outputs_preserved=True,hardware_gpu_acceptance=False,visual_acceptance=False)
        c.write(run/'process-report.json',state)
        c.write(run/'terminal-proof.json',dict(run_id=run.name,process_report_sha256=c.sha(run/'process-report.json'),complete=complete))
        (run/'wrapper.exit-code').write_text(str(code)+'\n')
    print(json.dumps(state,indent=2),flush=True)
    return code


if __name__=='__main__':
    sys.exit(main())
