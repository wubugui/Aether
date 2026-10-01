"""Bounded warm-cache continuation; original 180s failure remains immutable.

Uses the actual cloud display and existing project shader cache. Never saves a
scene. Preserve any observed project.godot newline normalization before restoring
only the byte-exact original; all other unexpected mutations fail the check.
"""
import json,os,tempfile,time,traceback
from pathlib import Path
import run_orbit61 as base


def cache_summary():
    files=[p for p in (base.PROJECT/'.godot').rglob('*') if p.is_file()]
    return dict(file_count=len(files),bytes=sum(p.stat().st_size for p in files),latest_mtime=max((p.stat().st_mtime for p in files),default=None))


def main():
    assert os.environ.get('DISPLAY'),'Actual cloud desktop required'
    assert not (base.PROJECT/'captures/request_editor_validation.flag').exists()
    assert base.digest(base.GODOT)=='db07cae7de644278a1884d4552bdf2bca3f5d30131b18faf3a0c4d730080b199'
    before=base.source_manifest(); project=base.PROJECT/'project.godot'; original=project.read_bytes()
    out=Path(tempfile.mkdtemp(prefix='nearbay61-import-v2-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-',dir=base.AETHER/'cloud-evidence'))
    data=Path(tempfile.mkdtemp(prefix='nearbay61-import-v2-',dir=base.ROOT/'tools-feiting'))
    # The old pinned manifest and unchanged prior resources remain in Git. Store
    # compact current additions, not another full duplicate of 1477 path rows.
    prior=json.loads(base.PRIOR.read_text())
    base.atomic_json(out/'input-binding.json',dict(prior_manifest_path=str(base.PRIOR.relative_to(base.AETHER)),prior_manifest_sha256=base.digest(base.PRIOR),prior_input_count=len(prior),additional_inputs={str(Path(p).relative_to(base.AETHER)):s for p,s in before.items() if p not in prior},total_input_count=len(before)))
    env=os.environ.copy();env.update(OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1')
    for key,folder in [('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config')]:
        path=data/folder;path.mkdir();env[key]=str(path)
    command=[str(base.GODOT),'--path',str(base.PROJECT),'--editor','--import','--quit','--rendering-method','gl_compatibility','--audio-driver','Dummy']
    state=dict(status='running',passed=False,run_id=out.name,timeout_seconds=600,command=command,cache_before=cache_summary(),scene_save_requested=False,visual_acceptance=False)
    base.atomic_json(out/'wrapper-report.json',state);print(out,flush=True)
    proc=None;error=None;observed_changes=[];normalized=False
    try:
        proc=base.child_run(command,out,env,600,'import')
    except BaseException:
        error=traceback.format_exc();(out/'wrapper-exception.log').write_text(error)
    finally:
        # Postcheck cannot strand a misleading running wrapper on a known
        # editor newline change. Preserve observed bytes before exact restore.
        for raw,sha in before.items():
            p=Path(raw);actual=base.digest(p) if p.is_file() else None
            if actual!=sha:observed_changes.append(dict(path=str(p.relative_to(base.AETHER)),before_sha256=sha,observed_sha256=actual))
        current=project.read_bytes()
        if current!=original and current==original.replace(b'\r\n',b'\n'):
            (out/'project.godot.observed-lf').write_bytes(current);project.write_bytes(original);normalized=True
        after={raw:base.digest(Path(raw)) if Path(raw).is_file() else None for raw in before}
        logs='\n'.join(p.read_text(errors='replace') for p in out.glob('*.log'))
        errors=[line for line in logs.splitlines() if line.startswith(('ERROR:','SCRIPT ERROR:')) or 'leaked' in line.lower()]
        renderer=[line for line in logs.splitlines() if any(w in line for w in ['OpenGL','Vulkan','llvmpipe','Rendering Device'])]
        process_complete=bool(proc and proc['returncode']==0 and not proc['timeout_triggered'] and proc['wrapper_received_signal'] is None)
        passed=process_complete and before==after and not errors and not error
        state.update(status='finished',passed=passed,import_process_completed=process_complete,process=proc,exception=error,sources_unchanged_after_exact_restoration=before==after,observed_source_changes=observed_changes,project_newline_normalization_restored=normalized,logged_errors=errors,renderer_lines=renderer,cache_after=cache_summary(),userdata=str(data),runtime_or_visual_acceptance=False)
        base.atomic_json(out/'wrapper-report.json',state);(out/'exit-code.txt').write_text('0\n' if passed else '1\n');print(json.dumps(state,indent=2),flush=True)
    return 0 if state['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
