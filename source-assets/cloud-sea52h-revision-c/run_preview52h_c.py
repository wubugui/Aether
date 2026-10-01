"""Run only after parent schedules the Blender graphics slot. No source saves."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,struct,subprocess,sys,tempfile,traceback
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
parser=argparse.ArgumentParser();parser.add_argument('--white',action='store_true');parser.add_argument('--variant',type=int,choices=[0],default=0);a=parser.parse_args()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudsea52h-c-source-v{a.variant}-{stamp}-',dir=ROOT/'cloud-evidence'))
(run/'images').mkdir();(run/'blender-config').mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[P/'cloud_sea52h_c.blend',P/'cloud_sea_52h_c_main_v0.glb',P/'preview52h_c.py',P/'run_preview52h_c.py',P/'geometry52h-c.json',BLENDER]
protected=[P/'cloud_sea52h_c.blend',P/'cloud_sea_52h_c_main_v0.glb']
protected += [p for dirname in ['cloud-sea52e','cloud-sea52f','cloud-sea52g','cloud-sea52h','cloud-sea52h-revision-b-plan','cloud-sea52h-revision-b'] for p in (P.parent/dirname).rglob('*') if p.is_file() and p.suffix in ('.blend','.glb')]
protected += [ROOT/'candidates/round40-exclusive-20260930/project/scenes/candidate52f/Game52f.tscn',ROOT/'candidates/round40-exclusive-20260930/project/project.godot',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend']
before={str(p):sha(p) for p in protected}
(run/'input-sha256.json').write_text(json.dumps({str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in inputs},indent=2))
command=[str(BLENDER),'-b','-t','2','--python-exit-code','1','--python',str(P/'preview52h_c.py'),'--','--out',str(run/'images'),'--variant',str(a.variant)]
if a.white:command.append('--white')
env=os.environ.copy();env.update({'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','BLENDER_USER_CONFIG':str(run/'blender-config')})
(run/'invocation.json').write_text(json.dumps({'argv':command,'cwd':str(ROOT),'started_utc':stamp,'white_diagnostic':a.white,'single_main_crown':True,'raw_union_comparison':False,'expected_images':5,'source_save':False},indent=2))
print(str(run),flush=True)
code=99
try:
    with (run/'stdout.log').open('wb') as out,(run/'stderr.log').open('wb') as err:
        proc=subprocess.Popen(command,cwd=ROOT,env=env,stdout=out,stderr=err)
        (run/'blender.pid').write_text(str(proc.pid));code=proc.wait()
except BaseException:
    (run/'wrapper-error.log').write_text(traceback.format_exc())
    raise
finally:
    (run/'blender-exitcode.txt').write_text(str(code)+'\n')
    after={str(p):sha(p) for p in protected}
    pngs=list((run/'images').glob('*.png'));pnginfo=[]
    for p in pngs:
        data=p.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';w,h=struct.unpack('>II',data[16:24]);pnginfo.append({'name':p.name,'width':w,'height':h,'bytes':len(data),'sha256':sha(p)})
    logs=(run/'stdout.log').read_text(errors='replace')+'\n'+(run/'stderr.log').read_text(errors='replace')
    hard_errors=[line for line in logs.splitlines() if line.startswith(('Error:','Traceback')) or 'Error: script failed' in line]
    success=code==0 and not hard_errors and before==after and len(pngs)==5 and all(p['width']==900 and p['height']==640 for p in pnginfo)
    (run/'result.json').write_text(json.dumps({'blender_exitcode':code,'complete':success,'hard_errors':hard_errors,'protected_unchanged':before==after,'protected_before':before,'protected_after':after,'images':pnginfo,'hardware_gpu_acceptance':False,'visual_acceptance':False,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    (run/'output-sha256.json').write_text(json.dumps({str(p.relative_to(run)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in run.rglob('*') if p.is_file() and 'blender-config' not in p.parts},indent=2))
    (run/'wrapper-exitcode.txt').write_text(('0' if success else '1')+'\n')
sys.exit(0 if success else 1)
