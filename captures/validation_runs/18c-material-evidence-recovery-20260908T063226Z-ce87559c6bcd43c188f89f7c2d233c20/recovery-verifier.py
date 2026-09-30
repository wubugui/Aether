"""Recover a collector path error without repeating completed GPU/flight work.

The original failed run is immutable and retained. This creates a separate
verification bundle, checks the actual producer report against its original
execution identity, and records that no engine stage was re-executed.
"""
from pathlib import Path
import shutil
from validation_manifest import (ValidationRun,exclusive_lock,read_json,require,
    sha256,snapshot_inputs,input_diff,validate_logs,validate_report,utc_now,write_json)

def main():
    root=Path(__file__).resolve().parents[1]
    source=root/'captures/validation_runs/18c-native-material-20260908T062423Z-e13cc07350264b9d800603025868e010'
    original=read_json(source/'manifest.json')
    require(original['status']=='failed' and original['passed'] is False,'Original collector must be terminal failed')
    require(original['error']=='stream-test: missing or stale report','Unexpected failure; do not bypass it')
    stages=original['stages']
    require([s['name'] for s in stages]==['import','capture-opening','capture-cliff-side','capture-cliff-back','capture-reverse','native-material','game-test','stream-test'],'Incomplete source execution')
    require(all(s['passed'] for s in stages[:-1]) and stages[-1]['exit_code']==0,'An engine stage failed')
    inputs=read_json(source/'inputs.json')['files']
    require(not input_diff(inputs,snapshot_inputs(root,imported=True)),'Source inputs changed since execution')
    producer=root/'captures/stream-flight-validation.json'
    last=stages[-1]
    require(producer.is_file() and last['started_ns']<=producer.stat().st_mtime_ns<=last['finished_ns'],'Producer report is not from the original execution window')
    report=read_json(producer)
    validate_report('stream-test',report,root,original['run_id'],inputs,last['started_ns'],last['finished_ns'],None)
    old_driver=source/'preparation/integrate_terrain_18c.py'
    corrected=root/'tools/integrate_terrain_18c.py'
    require(corrected.read_text()==old_driver.read_text().replace("('stream-test','stream-validation.json')","('stream-test','stream-flight-validation.json')"),'Collector changed beyond the path correction')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'18c-material-evidence-recovery',False,False)
        run.manifest.update(scope='Evidence recovery only: the source run executed all eight engine stages; its collector expected the wrong streaming filename. No engine, rendering or flight stage re-executed. Original failed manifest preserved.',
            source_run=str(source),source_run_id=original['run_id'],engine_stages_reexecuted=0,
            expected_counts={'native-material':7,'game-test':36,'stream-test':4})
        run.inputs=inputs
        try:
            for path,record in original['artifacts'].items():
                require(sha256(source/path)==record['sha256'],'Original evidence changed: '+path)
                target=run.directory/'source-run'/path;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(source/path,target);run.bind(target)
            for path,name in [(source/'manifest.json','original-failed-manifest.json'),(corrected,'corrected-collector.py'),(Path(__file__),'recovery-verifier.py')]:
                target=run.directory/name;shutil.copy2(path,target);run.bind(target)
            target=run.directory/'source-run/reports/stream-test.json';target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(producer,target);run.bind(target)
            verified=[]
            for stage in stages:
                validate_logs(source/(stage['name']+'.log'),source/(stage['name']+'-error.log'),stage['exit_code'])
                verified.append({'name':stage['name'],'original_exit_code':stage['exit_code'],
                    'original_status':stage['status'],'evidence_verified':True,
                    'report_binding_corrected':stage['name']=='stream-test'})
            native=read_json(source/'reports/native-material.json')
            require(native['passed'] and native['run_id']==original['run_id'] and len(native['checks'])==7 and all(c['passed'] for c in native['checks']),'Native material contract failed')
            game_stage=next(s for s in stages if s['name']=='game-test')
            validate_report('game-test',read_json(source/'reports/game-test.json'),root,original['run_id'],inputs,game_stage['started_ns'],game_stage['finished_ns'],None)
            run.assert_inputs()
            run.manifest.update(verified_source_stages=verified,underlying_engine_checks_passed=True,
                corrected_stream_report='source-run/reports/stream-test.json',original_manifest_preserved=True,
                input_count=len(inputs),status='passed',passed=True,completed_utc=utc_now())
            run.save()
            print('MATERIAL EVIDENCE RECOVERY PASS '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
