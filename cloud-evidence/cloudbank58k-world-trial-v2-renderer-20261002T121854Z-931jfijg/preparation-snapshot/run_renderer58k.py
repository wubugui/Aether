"""New explicit renderer admission for the verified relocated v1 work copy."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import tempfile
import time
import traceback
sys.dont_write_bytecode=True
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import binding58k as b


def validate_images(run,row):
    # This body is copied from the accepted v1 renderer result gate. The static
    # test normalizes only module aliases to prove its exact source equality.
    support=b.support;require=b.require;p=b.old.p;png_dimensions=b.old.png_dimensions
    native = support.strict_json(run/'images/report.json')
    require(native['passed'] is True and native['pid'] == row['pid'] and len(native['captures']) == 4,'Complete actual four-view result/PID')
    require(native['front_camera_is_inherited_1216'] is True and native['restored_to_original'] is True,'Original camera and opt-out verified')
    expected = ['01-original61-front','02-k-trial-front','03-k-fixed-side-back','04-k-fixed-near']
    require([x['name'] for x in native['captures']] == expected,'Fixed complete capture order')
    for item in native['captures']:
        image = run/'images'/(item['name']+'.png')
        require(support.sha(image) == item['image_sha256'] and image.stat().st_size == item['image_bytes'],'Actual PNG identity')
        # Each rendered state retains the already accepted native bytes.
        k = item['trial']; storage = k['k_storage']
        require(storage == dict(format=34359742471,vertex_count=1152,index_count=1152,
            vertex_data_sha256='6d3e3be9014ae790556976d1e40cf60ee460e9aa869efca6b9abce397f9b8262',
            index_data_sha256='ea7db52bc6c7f11cafcbaeb3043feac4593f2eed131d0a0ce9fe11e59fd46a2d'), 'Accepted K stored geometry remains exact at capture')
        material = k['k_material']
        accepted = support.strict_json(p.NATIVE/'native-reload.json')['material']
        require(material['albedo'] == accepted['albedo_srgb_rgba'] and all(material[key] == accepted[key] for key in ['roughness','metallic','cull_mode','transparency','texture_count','emission_enabled']), 'Original accepted native material values remain exact')
        require(material['standard'] and material['diffuse_mode'] == 0 and material['shading_mode'] == 1 and not material['vertex_color_use_as_albedo'] and not material['next_pass'] and not material['disable_fog'], 'Lit authored StandardMaterial with original fog and no substituted vertex-color override')
        expected_enabled = item['name'] != '01-original61-front'
        require(k['enabled'] == expected_enabled and k['k_visible'] == expected_enabled and k['old_visible'] != expected_enabled,'Only intended old/K visibility state')
        require(png_dimensions(image.read_bytes()) == item['resolution'] == [1179,664], 'Actual PNG IHDR and native Image retain fixed original viewport pixels')
    require(native['captures'][0]['camera_transform'] == native['captures'][1]['camera_transform'] and native['captures'][0]['camera_projection'] == native['captures'][1]['camera_projection'],'Original/K front identical camera and projection')
    require(native['captures'][0]['resolution'] == native['captures'][1]['resolution'], 'Original/K front actual PNG dimensions identical')
    require(all(x['reference'] == '1216' and x['weather_time'] == .35 for x in native['captures']),'Fixed inherited weather and actual time')


def main():
    parser=argparse.ArgumentParser();mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--run-approved-world-trial',action='store_true')
    mode.add_argument('--check-shared-copy',action='store_true')
    args=parser.parse_args()
    if not args.run_approved_world_trial and not args.check_shared_copy:
        print('Prepared v2 only; no migration, copy, display query or engine.');return 0
    expected,receipt=b.migrated_copy()
    if args.check_shared_copy:
        print(json.dumps(dict(passed=True,source=str(b.DESTINATION),members=len(expected),
            relative_manifest_sha256=b.canonical_sha(expected),engine_started=False),indent=2));return 0
    b.require(bool(os.environ.get('DISPLAY')),'Parent-provided existing graphical display required; no query or guess')
    b.require(not (b.HERE/'renderer-attempt.json').exists() and not (b.HERE/'renderer-terminal.json').exists(),'One new renderer admission only')
    with (b.HERE/'renderer-attempt.json').open('x') as f:
        json.dump(dict(pid=os.getpid(),shared_copy=str(b.DESTINATION)),f);f.flush();os.fsync(f.fileno())
    started=time.monotonic()
    run=Path(tempfile.mkdtemp(prefix='cloudbank58k-world-trial-v2-renderer-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=b.ROOT/'cloud-evidence'))
    print(run,flush=True)
    limits=b.old.LIMITS
    report=dict(version=b.VERSION,stage='renderer',passed=False,state='preparing',limits=limits,
        temporary_project=str(b.DESTINATION),v1_freeze_sha256=b.V1_FREEZE_SHA,
        v2_freeze_sha256=b.sha(b.HERE/'preparation-freeze.json'),native_scene_source_sha256=b.old.NATIVE_SHA,
        parse_report_sha256=b.PARSE_SHA,migration_receipt=receipt,images=0,
        world_geometry_saved=False,blender_started=False,glb_derived=False,editor_import_performed=False,
        visual_acceptance=False,hardware_gpu_acceptance=False)
    before={};handlers={}
    def stop(number,frame):raise InterruptedError('Wrapper signal '+str(number))
    try:
        for s in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):handlers[s]=signal.signal(s,stop)
        signal.setitimer(signal.ITIMER_REAL,limits['wrapper_seconds'])
        cpus=sorted(os.sched_getaffinity(0))[:2];b.require(len(cpus)==2,'Two CPUs required');os.sched_setaffinity(0,cpus)
        before=b.old.original.file_manifest(b.old.p.PROJECT)
        b.require(before==json.loads((b.old.p.NATIVE/'main-project-after.json').read_text()),'Current project equals successful v3 protection manifest')
        b.support.atomic_json(run/'main-project-before.json',before)
        b.support.atomic_json(run/'shared-project-before.json',b.inspect_tree(b.DESTINATION))
        shutil.copytree(b.HERE,run/'preparation-snapshot',ignore=shutil.ignore_patterns('__pycache__','*-attempt.json','*-terminal.json'))
        env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None)
        env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',LP_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
            path=run/name;path.mkdir();env[key]=str(path)
        command=[str(b.old.GODOT),'--path',str(b.DESTINATION),'--audio-driver','Dummy',
            '--rendering-method','gl_compatibility','--disable-vsync','--script','res://cloud_k_trial/observe58k.gd','--','--output-dir='+str(run/'images')]
        b.preparation();b.require(b.inspect_tree(b.DESTINATION)['files']==expected,'Exact relocated original parse files before renderer')
        remaining=limits['wrapper_seconds']-(time.monotonic()-started)-5
        b.require(remaining>=limits['renderer_child_seconds'],'Whole unchanged 240-second child budget remains')
        report['state']='running';b.support.atomic_json(run/'wrapper-report.json',report)
        row=b.support.run_child(command,run,env,b.DESTINATION,limits['renderer_child_seconds'],'renderer')
        report['process']=row
        b.require(b.support.process_passed(row),'Actual native process failed')
        b.require(not b.support.error_lines([run/'renderer.stdout.log',run/'renderer.stderr.log']),'Native log error/leak')
        validate_images(run,row)
        report.update(images=4,passed=True,state='completed')
    except BaseException:report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        try:
            after=b.old.original.file_manifest(b.old.p.PROJECT)
            report['main_project_unchanged']=bool(before and before==after)
            b.support.atomic_json(run/'main-project-after.json',after)
            b.support.atomic_json(run/'shared-project-after.json',b.inspect_tree(b.DESTINATION))
            b.preparation();report['frozen_inputs_unchanged']=True
            report['passed']=bool(report['passed'] and report['main_project_unchanged'])
        except BaseException:report.update(passed=False,finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL,0)
        for s,h in handlers.items():signal.signal(s,h)
        report['elapsed_seconds']=time.monotonic()-started
        report['logged_errors']=b.support.error_lines(sorted(run.glob('*.log')))
        if report['elapsed_seconds']>limits['wrapper_seconds'] or report['logged_errors']:report['passed']=False
        if not report['passed']:report['state']='failed'
        b.support.atomic_json(run/'wrapper-report.json',report)
        (run/'wrapper.exit-code').write_text('0\n' if report['passed'] else '1\n')
        b.support.atomic_json(b.HERE/'renderer-terminal.json',dict(passed=report['passed'],run=str(run),v2_freeze_sha256=report['v2_freeze_sha256'],wrapper_report_sha256=b.sha(run/'wrapper-report.json')))
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
