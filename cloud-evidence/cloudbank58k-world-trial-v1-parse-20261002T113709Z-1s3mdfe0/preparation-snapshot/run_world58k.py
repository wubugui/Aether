"""Prepare only by default; explicit one-shot parse or scheduled four-image trial."""
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import struct
import sys
import tempfile
import time
import traceback
sys.dont_write_bytecode = True
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import provenance58k as p
import world_support58k as support
sys.path.insert(0, str(HERE.parent/'import-v1'))
import run_import58k as original

ROOT = p.ROOT
GODOT = ROOT.parent/'tools-feiting/Godot_v4.5.1-stable_linux.x86_64'
ENGINE_SHA = 'db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
NATIVE_SHA = '91ab3412c67b5f82449396677a30a9bbe1542a338c00150dc1822910cdf7f789'
LIMITS = dict(parse_child_seconds=30, renderer_child_seconds=240, wrapper_seconds=300,
              cpus=2, maximum_aggregate_rss_kib=3145728, images=4, requested_window_width=1180, requested_window_height=664)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def png_dimensions(data):
    require(len(data) >= 33 and data[:8] == b'\x89PNG\r\n\x1a\n' and data[8:16] == b'\x00\x00\x00\rIHDR', 'Actual PNG IHDR required')
    return list(struct.unpack('>II', data[16:24]))


def preparation():
    freeze = support.strict_json(HERE/'preparation-freeze.json')
    for name, expected in freeze['files'].items():
        path = ROOT/name
        require(path.stat().st_size == expected['bytes'] and support.sha(path) == expected['sha256'], 'Frozen file changed: '+name)
    require(support.sha(GODOT) == ENGINE_SHA, 'Pinned official Godot binary')
    require(support.sha(p.NATIVE/'roundtrip.tscn') == NATIVE_SHA, 'Accepted saved K scene')
    plan = support.strict_json(HERE/'placement-provenance.json')
    require(plan['selected_root'] == 'CloudSea_1_1' and plan['anchor_world_xyz'] == [3958,0,3667], 'Fixed one-unit placement')
    return freeze


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--parse-only', action='store_true')
    mode.add_argument('--run-approved-world-trial', action='store_true')
    args = parser.parse_args()
    if not args.parse_only and not args.run_approved_world_trial:
        print('Prepared only; no engine, world copy, asset, or image created.')
        return 0
    stage = 'parse' if args.parse_only else 'renderer'
    preparation()
    prior_report = None
    if stage == 'renderer':
        require(bool(os.environ.get('DISPLAY')), 'Scheduled actual graphical display required')
        prior = support.strict_json(HERE/'parse-terminal.json')
        require(prior['passed'] is True and prior['freeze_sha256'] == support.sha(HERE/'preparation-freeze.json'), 'Successful same-freeze parse required')
        prior_path = Path(prior['run'])/'wrapper-report.json'
        require(support.sha(prior_path) == prior['wrapper_report_sha256'], 'Exact completed parse report')
        prior_report = support.strict_json(prior_path)
        require(prior_report['passed'] is True, 'Actual successful parse result')
    require(not (HERE/(stage+'-terminal.json')).exists(), 'Existing terminal preserved; no rerun')
    with (HERE/(stage+'-attempt.json')).open('x') as f:
        json.dump(dict(pid=os.getpid(), admitted_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())),f)
        f.flush(); os.fsync(f.fileno())
    started = time.monotonic()
    run = Path(tempfile.mkdtemp(prefix='cloudbank58k-world-trial-v1-'+stage+'-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=ROOT/'cloud-evidence'))
    print(run,flush=True)
    report = dict(version='cloud58k-world-trial-v1', stage=stage, passed=False, state='preparing', limits=LIMITS,
                  native_scene_source_sha256=NATIVE_SHA, freeze_sha256=support.sha(HERE/'preparation-freeze.json'),
                  images=0, world_geometry_saved=False, blender_started=False, glb_derived=False,
                  visual_acceptance=False, hardware_gpu_acceptance=False)
    before = {}; scratch = None; handlers = {}
    def stop(number, frame):
        raise InterruptedError('Wrapper signal '+str(number))
    try:
        for s in (signal.SIGINT,signal.SIGTERM,signal.SIGALRM):
            handlers[s] = signal.signal(s,stop)
        signal.setitimer(signal.ITIMER_REAL,LIMITS['wrapper_seconds'])
        cpus = sorted(os.sched_getaffinity(0))[:2]
        require(len(cpus) == 2, 'Two CPUs required')
        os.sched_setaffinity(0,cpus)
        before = original.file_manifest(p.PROJECT)
        require(before == json.loads((p.NATIVE/'main-project-after.json').read_text()), 'Current project equals successful v3 protection manifest')
        support.atomic_json(run/'main-project-before.json',before)
        shutil.copytree(HERE,run/'preparation-snapshot',ignore=shutil.ignore_patterns('__pycache__','*-attempt.json','*-terminal.json'))
        if stage == 'parse':
            scratch = Path(tempfile.mkdtemp(prefix='cloud58k-world-trial-v1-',dir='/tmp'))
            # Exactly one work copy, reused by this freeze's subsequent renderer.
            # No symlink/hardlink can expose the accepted project to engine writes.
            shutil.copytree(p.PROJECT,scratch,dirs_exist_ok=True)
            trial = scratch/'cloud_k_trial'; trial.mkdir()
            for name in ('trial58k.gd','observe58k.gd','parse58k.gd'):
                shutil.copy2(HERE/name,trial/name)
            shutil.copy2(HERE/'CloudKTrial.tscn.template',trial/'CloudKTrial.tscn')
            shutil.copy2(p.NATIVE/'roundtrip.tscn',trial/'accepted-native-k.tscn')
        else:
            scratch = Path(prior_report['temporary_project'])
            require(scratch.parent == Path('/tmp') and scratch.name.startswith('cloud58k-world-trial-v1-') and scratch.is_dir(), 'Same isolated parse work copy must exist')
            manifest_path = Path(prior['run'])/'temporary-project-after.json'
            require(support.sha(manifest_path) == prior_report['temporary_project_manifest_sha256'], 'Bound parse work-copy manifest')
            require(original.file_manifest(scratch) == support.strict_json(manifest_path), 'Same unchanged work copy; no recopy/fallback')
        report['temporary_project'] = str(scratch)
        env = os.environ.copy(); env.pop('PYTHONOPTIMIZE',None)
        env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',NUMEXPR_NUM_THREADS='2',LP_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1')
        for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
            path = run/name;path.mkdir();env[key] = str(path)
        command = [str(GODOT),'--path',str(scratch),'--audio-driver','Dummy']
        if stage == 'parse':
            command += ['--headless','--check-only','--script','res://cloud_k_trial/parse58k.gd']
            budget = LIMITS['parse_child_seconds']
        else:
            command += ['--rendering-method','gl_compatibility','--disable-vsync','--script','res://cloud_k_trial/observe58k.gd','--','--output-dir='+str(run/'images')]
            budget = LIMITS['renderer_child_seconds']
        preparation()
        remaining = LIMITS['wrapper_seconds']-(time.monotonic()-started)-5
        require(remaining >= budget,'Whole scheduled child budget remains after preparation/copy')
        report['state'] = 'running'; support.atomic_json(run/'wrapper-report.json',report)
        row = support.run_child(command,run,env,scratch,budget,stage)
        report['process'] = row
        require(support.process_passed(row),'Actual native process failed')
        require(not support.error_lines([run/(stage+'.stdout.log'),run/(stage+'.stderr.log')]),'Native log error/leak')
        if stage == 'renderer':
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
            report['images'] = 4
        report.update(passed=True,state='completed')
    except BaseException:
        report.update(passed=False,state='failed',error=traceback.format_exc())
    finally:
        try:
            after = original.file_manifest(p.PROJECT)
            report['main_project_unchanged'] = bool(before and before == after)
            support.atomic_json(run/'main-project-after.json',after)
            if scratch is not None:
                support.atomic_json(run/'temporary-project-after.json',original.file_manifest(scratch))
                report['temporary_project_manifest_sha256'] = support.sha(run/'temporary-project-after.json')
            preparation(); report['frozen_inputs_unchanged'] = True
            report['passed'] = bool(report['passed'] and report['main_project_unchanged'])
        except BaseException:
            report.update(passed=False,finalization_error=traceback.format_exc())
        signal.setitimer(signal.ITIMER_REAL,0)
        for s,h in handlers.items(): signal.signal(s,h)
        report['elapsed_seconds'] = time.monotonic()-started
        report['logged_errors'] = support.error_lines(sorted(run.glob('*.log')))
        if report['elapsed_seconds'] > LIMITS['wrapper_seconds'] or report['logged_errors']: report['passed'] = False
        if not report['passed']: report['state'] = 'failed'
        support.atomic_json(run/'wrapper-report.json',report)
        (run/'wrapper.exit-code').write_text('0\n' if report['passed'] else '1\n')
        support.atomic_json(HERE/(stage+'-terminal.json'),dict(passed=report['passed'],run=str(run),freeze_sha256=report['freeze_sha256'],wrapper_report_sha256=support.sha(run/'wrapper-report.json')))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
