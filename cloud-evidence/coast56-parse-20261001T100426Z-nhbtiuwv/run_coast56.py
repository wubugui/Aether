#!/usr/bin/env python3
"""Default: parse only. Actual GL build and fresh-process verify are separate explicit stages.
Never start a renderer with the default command. No full-scene packing or default promotion.
"""
from __future__ import annotations
import argparse,hashlib,json,os,signal,subprocess,time,tempfile,shutil
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2];P=R/'candidates/round40-exclusive-20260930/project';T=R.parent/'tools-feiting';GODOT=T/'Godot_v4.5.1-stable_linux.x86_64'
SCRIPTS={'build':D/'build_coast56.gd','verify':D/'verify_coast56.gd'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):
 tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2));tmp.replace(p)
def main():
 ap=argparse.ArgumentParser(description=__doc__);modes=ap.add_mutually_exclusive_group();modes.add_argument('--parse-only',action='store_true');modes.add_argument('--build-renderer',action='store_true');modes.add_argument('--verify-renderer',action='store_true');ap.add_argument('--wall-timeout',type=float,default=600);args=ap.parse_args()
 mode='build' if args.build_renderer else ('verify' if args.verify_renderer else 'parse')
 if mode!='parse' and not os.environ.get('DISPLAY'):raise SystemExit('Real GL stage requires the actual connected display; no fallback to headless saving')
 manifest=json.loads((D/'preparation-manifest.json').read_text());immutable=manifest['immutable_inputs']
 for path,digest in immutable.items():
  if sha(path)!=digest:raise SystemExit('Immutable input changed: '+path)
 out=Path(tempfile.mkdtemp(prefix=f'coast56-{mode}-{time.strftime("%Y%m%dT%H%M%SZ",time.gmtime())}-',dir=R/'cloud-evidence'));print(out,flush=True)
 env=os.environ.copy();env['COAST56_OUT']=str(out)
 for key,name in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
  p=T/'userdata'/name;p.mkdir(parents=True,exist_ok=True);env[key]=str(p)
 before={**immutable,**{str(p):sha(p) for p in [Path(__file__).resolve(),D/'coast56_common.gd',*SCRIPTS.values()]}}
 write(out/'input-sha256.json',before)
 for path in [Path(__file__).resolve(),D/'coast56_common.gd',*SCRIPTS.values(),D/'preparation-manifest.json',D/'Game56Coast.tscn.template']:shutil.copy2(path,out/path.name)
 stages=['build','verify'] if mode=='parse' else [mode];records=[];ok=True
 for stage in stages:
  command=[str(GODOT),'--path',str(P)]
  if mode=='parse':command+=['--headless','--check-only']
  else:command+=['--rendering-method','gl_compatibility','--audio-driver','Dummy','--disable-vsync']
  command+=['--script',str(SCRIPTS[stage])]
  rec={'stage':stage,'mode':mode,'command':command,'started':False,'finished':False,'max_rss_kib':None,'renderer_executed':mode!='parse','visual_acceptance':False,'source_scene_mutation_allowed':False,'allowed_build_outputs':'Only independent assets/coast56 six resources and tiny scenes/candidate56-coast, plus evidence' if mode=='build' else 'No project writes'};records.append(rec);write(out/'wrapper-report.json',{'mode':mode,'records':records,'passed':False})
  start=time.monotonic();termination=None;interrupted=None
  with (out/f'{stage}.stdout.log').open('wb') as stdout,(out/f'{stage}.stderr.log').open('wb') as stderr:
   child=subprocess.Popen(command,env=env,cwd=P,stdout=stdout,stderr=stderr,start_new_session=True);rec.update(started=True,pid=child.pid)
   def stop(sig,frame):
    nonlocal termination,interrupted
    interrupted=sig;termination=time.monotonic()
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
   old={sig:signal.signal(sig,stop) for sig in [signal.SIGINT,signal.SIGTERM]}
   while True:
    waited,status,usage=os.wait4(child.pid,os.WNOHANG)
    if waited:
     child.returncode=os.waitstatus_to_exitcode(status);break
    now=time.monotonic()
    if now-start>args.wall_timeout and termination is None:
     termination=now;rec['timeout']=True;os.killpg(child.pid,signal.SIGTERM)
    if termination is not None and now-termination>10:
     try:os.killpg(child.pid,signal.SIGKILL)
     except ProcessLookupError:pass
    time.sleep(.1)
   for sig,handler in old.items():signal.signal(sig,handler)
  logs=(out/f'{stage}.stdout.log').read_text(errors='replace')+'\n'+(out/f'{stage}.stderr.log').read_text(errors='replace')
  errors=[line for line in logs.splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
  rec.update(finished=True,exit_code=child.returncode,signal=-child.returncode if child.returncode<0 else None,max_rss_kib=usage.ru_maxrss,elapsed_seconds=time.monotonic()-start,errors=errors,interrupted=interrupted)
  stage_ok=child.returncode==0 and not errors and all(sha(path)==digest for path,digest in before.items())
  if mode!='parse':
   report_name='build-report56.json' if stage=='build' else 'verify-report56.json'
   try:stage_ok=stage_ok and json.loads((out/report_name).read_text()).get('passed') is True
   except (OSError,ValueError):stage_ok=False
  rec['passed']=stage_ok;ok=ok and stage_ok;write(out/'wrapper-report.json',{'mode':mode,'records':records,'passed':ok,'parse_is_not_runtime_verification':mode=='parse'})
  if not stage_ok:break
 (out/'exit-code.txt').write_text('0' if ok else '1');(D/'last-'+mode+'.txt').write_text(str(out)+'\n') if False else None
 print('COAST56',mode,'PASSED' if ok else 'FAILED',out,flush=True);return 0 if ok else 1
if __name__=='__main__':raise SystemExit(main())
