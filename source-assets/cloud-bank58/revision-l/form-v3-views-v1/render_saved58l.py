"""Render-only adapter. Open the existing source; no build/save/export path."""
from __future__ import annotations
import argparse, os, sys, traceback
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import views58l as v
n, s, g = v.native, v.s, v.g
capture, write, sha, emit = n.capture, n.write, n.sha, n.emit

def main(arguments=None):
    args = arguments if arguments is not None else (sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['render']); ap.add_argument('--view', choices=v.VIEWS)
    ap.add_argument('--out', type=Path); ap.add_argument('--admission', type=Path)
    a = ap.parse_args(args)
    if a.mode is None:
        print('No-op: new render-only admission required; no engine import or action.')
        return 0
    v.require(a.out is not None and a.admission is not None and a.view in v.VIEWS, 'Explicit render-only admission')
    runtime = v.runtime(native_process=True)
    v.verify_admission(v.read(a.admission), a.admission, a.out, a.view)
    v.require_source()
    label = 'render-' + a.view
    n._TELEMETRY = (a.out, label)
    emit('native_entry', mode='render', views_stage=v.STAGE, views_version=v.VERSION)
    report = dict(acceptance_mode=s.DIAGNOSTIC_MODE, full_native_acceptance=False, diagnostic_acceptance=False,
                  historical_default_failure=dict(s.HISTORICAL_DEFAULT_FAILURE),
                  historical_form_v2_default_failure=dict(s.HISTORICAL_FORM_V2_DEFAULT_FAILURE), version=g.VERSION,
                  views_version=v.VERSION, views_stage=v.STAGE, original_source_stage='failed',
                  admission_sha256=v.sha(a.admission), adapter_sha256=v.sha(Path(__file__)),
                  source_native_sha256=v.sha(v.FORM / 'native58l.py'), runtime=runtime,
                  mode='render', view=a.view, pid=os.getpid(), passed=False, state='started', source_saved=False,
                  images=0, world_loaded=False, world_integration_allowed=False, contact_acceptance=False,
                  world_acceptance=False, global_GOAL=False, visual_acceptance=False, weather_acceptance=False)
    try:
        import bpy
        c, b = v.read(g.CANDIDATE_PATH), v.read(g.BINDING_PATH)
        emit('candidate_validation.begin'); g.validate_candidate(c); emit('candidate_validation.complete')
        emit('fresh_open.begin'); bpy.context.preferences.filepaths.use_scripts_auto_execute = False
        bpy.ops.wm.open_mainfile(filepath=str(g.SOURCE), load_ui=False, use_scripts=False)
        emit('fresh_open.complete', opened_filepath=bpy.data.filepath)
        v.require(Path(bpy.data.filepath).resolve() == g.SOURCE, 'Actually opened original saved source')
        v.require_source()
        raw = capture(c, g); rawpath = a.out / (label + '-raw.json')
        write(rawpath, raw, True); report.update(raw_path=str(rawpath), raw_sha256=sha(rawpath))
        write(a.out / (label + '-result.json'), report)
        report['validation'] = g.validate_native_raw(raw, c, b)
        v.require(s.identity(raw) == s.identity(v.read(v.SOURCE_RUN / 'outputs/build-raw.json')), 'Original saved form-v3 source numeric identity')
        s.require(a.view in [r['name'] for r in b['world_cameras']],'Exactly one original absolute camera');scene=bpy.context.scene;original_camera=scene.camera;original_filepath=scene.render.filepath;original_images=set(bpy.data.images.keys());scene.camera=bpy.data.objects[s.CAMERA_PREFIX+a.view];path=a.out/(a.view+'.png');scene.render.filepath=str(path);emit('render.begin',view=a.view);bpy.ops.render.render(write_still=True);emit('render.complete',view=a.view);report.update(images=1,image_sha256=sha(path),image_path=str(path),source_diagnostic_only=True)
        rendered=capture(c,g);rendered_path=a.out/(label+'-rendered-raw.json');write(rendered_path,rendered,True);report['rendered_raw_sha256']=sha(rendered_path);report['rendered_normals']=s.validate_normals(rendered['mesh'])
        for img in list(bpy.data.images):
            if img.name not in original_images:
                s.require(img.type=='RENDER_RESULT' and img.source=='VIEWER','Only native transient render result may be released');bpy.data.images.remove(img)
        scene.camera=original_camera;scene.render.filepath=original_filepath;bpy.context.view_layer.update();restored=capture(c,g);rp=a.out/(label+'-restored-raw.json');write(rp,restored,True);s.require(s.identity(restored)==s.identity(raw),'Exact source camera/scene identity restored after render');report.update(restored_raw_sha256=sha(rp),exact_identity_restored=True,restored_validation=s.validate_capture(restored,c,b,s.expected_texts(g.HERE,c,b)))
        v.require_source()
        report.update(passed=True, diagnostic_acceptance=True, state='completed', source_sha256=v.SOURCE_SHA, source_bytes=v.SOURCE_BYTES)
    except BaseException:
        report.update(state='failed', error=traceback.format_exc())
        try:
            failure_path = a.out / (label + '-failure-raw.json')
            write(failure_path, capture(c, g), True); report['failure_raw_sha256'] = sha(failure_path)
        except BaseException:
            report['failure_capture_error'] = traceback.format_exc()
        raise
    finally:
        emit('native_terminal', passed=report['passed'], state=report['state'])
        write(a.out / (label + '-result.json'), report)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
