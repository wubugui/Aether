#!/usr/bin/env python3
"""Source-only default. Explicit --run-approved-import performs one bounded native trial."""
import argparse
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
import traceback
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
# Keep the supervisor single-threaded before NumPy can initialize BLAS;
# native children receive their separate CPU2/thread2 environment below.
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import contract58k as c
import bounded_support58k as support

TOTAL_SECONDS=120
NATIVE_SECONDS=(30,30,20,20)
PROJECT=c.ROOT/'candidates/round40-exclusive-20260930/project'
PROJECT_TEXT='''config_version=5
[application]
config/name="Isolated cloud58K import validation"
[rendering]
renderer/rendering_method="gl_compatibility"
[threading]
worker_pool/max_threads=2
'''
IMPORT_PARAMETERS={
 'nodes/root_type':'Node3D','nodes/root_name':'Cloud58K_Import',
 'nodes/apply_root_scale':True,'nodes/root_scale':1.0,
 'meshes/ensure_tangents':False,'meshes/generate_lods':False,
 'meshes/create_shadow_meshes':False,'meshes/light_baking':0,
 'meshes/force_disable_compression':True,'animation/import':False,
 'import_script/path':'','materials/extract':0,'_subresources':{},'gltf/naming_version':2,'gltf/embedded_image_handling':0}

def file_manifest(root):
    result={}
    for path in sorted(root.rglob('*')):
        if path.is_symlink():raise ValueError('Symlink in protected/project tree: '+str(path))
        if path.is_file():result[str(path)]=c.sha(path)
    return result

def frozen_inputs():
    freeze=c.HERE/'preparation-freeze58k.json';data=c.read(freeze)
    result={str(c.ROOT/path):row['sha256'] for path,row in data['files'].items()}
    result[str(freeze)]=c.sha(freeze)
    observed,changed,errors=support.inspect_inputs(result)
    c.require(not changed and not errors,'Preparation/protected identity mismatch '+repr(changed+errors))
    return result

def output_files(scratch):
    return {str(p.relative_to(scratch)):{'bytes':p.stat().st_size,'sha256':c.sha(p)} for p in sorted(scratch.rglob('*')) if p.is_file()}

def native_report(path,mode):
    report=c.read(path)
    c.require(report['passed'] is True and report['version']=='cloud58k-import-v1' and report['mode']==mode,'Native report explicit successful completion')
    c.require(report['world_loaded'] is False and report['images']==0,'Native isolated resource-only scope')
    c.require([report['engine'][k] for k in ('major','minor','patch')]==[4,5,1],'Actual engine version')
    return report

def validate_native(report,source):
    geometry=c.validate_geometry(report['geometry'],source,clockwise=True)
    material=c.validate_material(report['material'],source,godot=True)
    c.require(max(abs(x-y) for a,b in zip(report['aabb'],geometry['godot_relative_bounds']) for x,y in zip(a,b))<=c.POSITION_EPS,'Godot actual mesh AABB')
    for row in report['transforms']:
        c.require(row['origin']==[0,0,0] and row['basis']==[[1,0,0],[0,1,0],[0,0,1]],'No origin/basis rewrite')
    return dict(geometry=geometry,material=material)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-approved-import',action='store_true');args=parser.parse_args()
    if not args.run_approved_import:
        print('Prepared source only; no export, engine, image or project mutation. Native trial requires parent scheduling.');return 0
    c.require(not (c.HERE/'native-terminal58k.json').exists(),'Existing attempted trial retained; do not rerun v1 in place')
    # Persistent exclusive admission: also prevents concurrent launch and retry after SIGKILL.
    with (c.HERE/'native-attempt58k.json').open('x') as admitted:
        c.json.dump(dict(pid=os.getpid(),time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),state='admitted_one_shot_not_a_completion_report'),admitted)
        admitted.flush();os.fsync(admitted.fileno())
    started=time.monotonic();run=Path(tempfile.mkdtemp(prefix='cloudbank58k-import-v1-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=c.ROOT/'cloud-evidence'))
    print(run,flush=True)
    report=dict(version='cloud58k-import-v1',passed=False,state='preparing',run=str(run),limits=dict(total_seconds=TOTAL_SECONDS,native_stage_seconds=list(NATIVE_SECONDS),cpu_threads=2,max_wrapper_plus_child_rss_kib=support.MAX_RSS_KIB,max_glb_bytes=c.MAX_GLB_BYTES),stages=[],world_loaded=False,world_anchor_applied=False,images=0,visual_acceptance=False)
    before={};protected={};scratch=None
    old_handlers={}
    def stop(number,_frame):raise InterruptedError('Wrapper signal '+str(number))
    try:
        for number in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):old_handlers[number]=signal.signal(number,stop)
        signal.setitimer(signal.ITIMER_REAL,TOTAL_SECONDS)
        cpus=sorted(os.sched_getaffinity(0))[:2];c.require(len(cpus)==2,'CPU2 available');os.sched_setaffinity(0,cpus)
        before=frozen_inputs();c.source_preconditions()
        c.require(c.sha(c.BLENDER)==c.BLENDER_SHA and c.sha(c.GODOT)==c.GODOT_SHA,'Official pinned executable identities')
        protected=file_manifest(PROJECT) # Includes every original .godot/cache and import sidecar.
        support.atomic_json(run/'main-project-before.json',protected)
        support.atomic_json(run/'input-sha256.json',before)
        shutil.copytree(c.HERE,run/'preparation-snapshot',ignore=shutil.ignore_patterns('__pycache__'))
        scratch=Path(tempfile.mkdtemp(prefix='cloud58k-import-v1-',dir='/tmp'));report['temporary_project']=str(scratch)
        (scratch/'project.godot').write_text(PROJECT_TEXT)
        shutil.copy2(c.HERE/'probe58k.gd',scratch/'probe58k.gd')
        (run/'export').mkdir()
        env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
        env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data'),('BLENDER_USER_CONFIG','blender-config')]:
            path=run/name;path.mkdir();env[key]=str(path)
        commands=[
          [str(c.BLENDER),'--factory-startup','--disable-autoexec','-b','-t','2','--python-exit-code','1','--python',str(c.HERE/'export58k.py'),'--','--out',str(run/'export')],
          [str(c.GODOT),'--headless','--editor','--path',str(scratch),'--import'],
          [str(c.GODOT),'--headless','--path',str(scratch),'--script','res://probe58k.gd','--','import',str(run/'godot-import.json')],
          [str(c.GODOT),'--headless','--path',str(scratch),'--script','res://probe58k.gd','--','reload',str(run/'godot-reload.json')]]
        labels=['blender-export','godot-editor-import','godot-import-readback','godot-fresh-reload']
        artifact_hashes={p:c.sha(p) for p in [scratch/'project.godot',scratch/'probe58k.gd']}
        for index,(command,label,cap) in enumerate(zip(commands,labels,NATIVE_SECONDS)):
            c.require(frozen_inputs()==before,'Inputs changed before native stage')
            c.require(all(c.sha(path)==digest for path,digest in artifact_hashes.items()),'Earlier stage outputs changed')
            remaining=TOTAL_SECONDS-(time.monotonic()-started)-3
            c.require(remaining>0,'Total budget exhausted')
            report['state']='running';support.atomic_json(run/'wrapper-report.json',report)
            row=support.run_child(command,run,env,scratch,min(cap,remaining),label)
            report['stages'].append(row);support.atomic_json(run/'wrapper-report.json',report)
            c.require(support.process_passed(row),'Native stage failed: '+label)
            c.require(not support.error_lines([run/(label+'.stdout.log'),run/(label+'.stderr.log')]),'Native logged error/leak')
            if index==0:
                source=c.read(run/'export/source-readback.json');c.require(source['pid']==row['pid'],'Blender report PID matches actual process');c.require(source['passed'] and source['source_sha256']==c.SOURCE_SHA,'Actual Blender readback report')
                doc,raw,mat=c.parse_glb(run/'export/cloud58k.glb');report['export_geometry']=c.validate_geometry(raw,source);report['export_material']=c.validate_material(mat,source)
                shutil.copy2(run/'export/cloud58k.glb',scratch/'cloud58k.glb')
                lines=['[remap]','importer="scene"','importer_version=1','type="PackedScene"','','[deps]','source_file="res://cloud58k.glb"','','[params]']
                for key,value in IMPORT_PARAMETERS.items():lines.append(key+'='+c.json.dumps(value,separators=(',',':')))
                (scratch/'cloud58k.glb.import').write_text('\n'.join(lines)+'\n')
                artifact_hashes.update({p:c.sha(p) for p in [run/'export/cloud58k.glb',run/'export/source-readback.json',scratch/'cloud58k.glb']})
            elif index==1:
                c.require((scratch/'cloud58k.glb.import').is_file() and (scratch/'.godot/imported').is_dir(),'Actual isolated import outputs')
            elif index==2:
                imported=native_report(run/'godot-import.json','import');c.require(imported['pid']==row['pid'],'Godot import report PID matches actual process');report['import_validation']=validate_native(imported,source)
                c.require(imported['roundtrip_saved'] is True,'Native snapshot saved')
                c.require(all(imported['import_settings'].get(k)==v for k,v in IMPORT_PARAMETERS.items()),'Actual importer options applied')
                c.require((scratch/'roundtrip.tscn').stat().st_size<=500000,'Native roundtrip size cap')
                c.require('[ext_resource' not in (scratch/'roundtrip.tscn').read_text(),'Native roundtrip must have embedded resources only')
                artifact_hashes.update({p:c.sha(p) for p in [run/'godot-import.json',scratch/'roundtrip.tscn',scratch/'cloud58k.glb.import']})
            else:
                reloaded=native_report(run/'godot-reload.json','reload');c.require(reloaded['pid']==row['pid'],'Godot reload report PID matches actual process');report['reload_validation']=validate_native(reloaded,source)
                c.require(reloaded['pid']!=imported['pid'],'Independent process reload')
                c.require(not reloaded['dependencies'],'Native roundtrip has no external resource dependencies')
                c.require(all(reloaded[k]==imported[k] for k in ('geometry','material','transforms','aabb')),'Exact native save/fresh-load arrays/material/transform identity')
        c.require(all(c.sha(path)==digest for path,digest in artifact_hashes.items()),'Frozen outputs changed after final native stage')
        report['passed']=True;report['state']='completed'
    except BaseException:
        report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        # No child remains; retain wall watchdog during identity/readback finalization.
        try:
            _,changed,errors=support.inspect_inputs(before)
            after=file_manifest(PROJECT)
            report.update(inputs_unchanged=bool(before and not changed and not errors),changed_inputs=changed,input_read_errors=errors,main_project_unchanged=bool(protected and protected==after),source_unchanged=c.sha(c.SOURCE)==c.SOURCE_SHA)
            report['passed']=bool(report['passed'] and report['inputs_unchanged'] and report['main_project_unchanged'] and report['source_unchanged'])
            support.atomic_json(run/'main-project-after.json',after)
            if scratch:
                report['temporary_project_manifest']=output_files(scratch)
                # Small native outputs are preserved in evidence; temporary .godot is retained in /tmp.
                for filename in ['project.godot','cloud58k.glb.import','roundtrip.tscn']:
                    if (scratch/filename).is_file():shutil.copy2(scratch/filename,run/filename)
        except BaseException:
            report.update(passed=False,finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL,0)
        for sig,handler in old_handlers.items():signal.signal(sig,handler)
        report['elapsed_seconds']=time.monotonic()-started
        if report['elapsed_seconds']>TOTAL_SECONDS:report['passed']=False
        report['logged_errors']=support.error_lines(sorted(run.glob('*.log')))
        if report['logged_errors']:report['passed']=False
        support.atomic_json(run/'wrapper-report.json',report)
        (run/'wrapper.exit-code').write_text('0\n' if report['passed'] else '1\n')
        c.write(c.HERE/'native-terminal58k.json',dict(passed=report['passed'],run=str(run),wrapper_report_sha256=c.sha(run/'wrapper-report.json')))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
