"""Run only after parent schedules the Blender graphics slot. No source saves."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,struct,subprocess,sys,tempfile,traceback
P=Path(__file__).resolve().parent;ROOT=P.parent.parent
BLENDER=ROOT.parent/'tools-feiting/blender-4.5.14-linux-x64/blender'
parser=argparse.ArgumentParser();parser.add_argument('--white',action='store_true');a=parser.parse_args()
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
run=Path(tempfile.mkdtemp(prefix=f'cloudsea52c-source-v0-{stamp}-',dir=ROOT/'cloud-evidence'))
(run/'images').mkdir();(run/'blender-config').mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[P/'cloud_sea52c.blend',P/'cloud_sea_52c_0.glb',P/'preview_sea52c.py',P/'run_preview52c.py',P/'geometry52c.json',BLENDER]
protected=[P/'cloud_sea52c.blend',ROOT/'blender/cliff_kit/cliff_eastern_plateau.blend',ROOT/'candidates/round40-exclusive-20260930/source-assets/cloud-sea46/cloud_sea46.blend']
before={str(p):sha(p) for p in protected}
(run/'input-sha256.json').write_text(json.dumps({str(p):{'sha256':sha(p),'bytes':p.stat().st_size} for p in inputs},indent=2))
command=[str(BLENDER),'-b','-t','4','--python-exit-code','1','--python',str(P/'preview_sea52c.py'),'--','--out',str(run/'images'),'--variant','0']
if a.white:command.append('--white')
env=os.environ.copy();env.update({'OMP_NUM_THREADS':'4','OPENBLAS_NUM_THREADS':'4','BLENDER_USER_CONFIG':str(run/'blender-config')})
(run/'invocation.json').write_text(json.dumps({'argv':command,'cwd':str(ROOT),'started_utc':stamp,'white_diagnostic':a.white,'expected_images':5,'source_save':False},indent=2))
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
    success=code==0 and before==after and len(pngs)==5 and all(p['width']==900 and p['height']==640 for p in pnginfo)
    (run/'result.json').write_text(json.dumps({'blender_exitcode':code,'complete':success,'protected_unchanged':before==after,'protected_before':before,'protected_after':after,'images':pnginfo,'hardware_gpu_acceptance':False,'visual_acceptance':False,'finished_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
    (run/'output-sha256.json').write_text(json.dumps({str(p.relative_to(run)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in run.rglob('*') if p.is_file() and 'blender-config' not in p.parts},indent=2))
    (run/'wrapper-exitcode.txt').write_text(('0' if success else '1')+'\n')
sys.exit(0 if success else 1)
