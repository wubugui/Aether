"""Scoped verification of the five new cliff assets; this is not a release run."""
import sys,shutil
from pathlib import Path
root=Path('D:/test6');sys.path.insert(0,str(root/'tools'))
from validation_manifest import ValidationRun,exclusive_lock,snapshot_inputs,write_json,utc_now,require,sha256
from validate_section_overlap import validate_section_overlap
with exclusive_lock(root/'captures/.validation-pipeline.lock'):
    run=ValidationRun(root,'10a-cliff-edit',False,True)
    run.manifest['scope']='Five remodeled cliff assets: source images, game checks, cliff contacts and circumnavigation. No Windows export, no new long-distance or road acceptance.'
    run.manifest['release_validation']=False
    run.manifest['expected_counts']={k:run.manifest['expected_counts'][k] for k in ['game-test','cliffs-contact','cliff-tour-test','geology']}
    shutil.copy2(__file__,run.directory/'scoped-driver.py');run.bind(run.directory/'scoped-driver.py')
    try:
        run.inputs=snapshot_inputs(root,imported=True)
        write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs})
        run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(run.inputs);run.save()
        engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe';marker='--validation-run='+run.run_id
        required=set()
        for view in ['opening','cliff-back','cliff-side','reverse']:
            name='capture-'+view;required.add(name);output=run.directory/'images'/(view+'.png')
            run.stage(name,[engine,'--path',root,'--','--capture','--view='+view,'--output='+str(output),marker],image=output)
        required.add('reference-metrics')
        run.stage('reference-metrics',[sys.executable,'tools/compare_reference.py','--candidate',run.directory/'images/opening.png','--round',run.run_id],report=root/'reviews'/('round-'+run.run_id+'-metrics.json'),metrics=True)
        for name,sink in [('game-test','game-validation.json'),('cliff-tour-test','cliff-tour-validation.json')]:
            required.add(name);run.stage(name,[engine,'--path',root,'--','--'+name,marker],report=root/'captures'/sink)
        required.add('cliffs-contact')
        run.stage('cliffs-contact',[engine,'--path',root,'--script','tools/verify_cliff_flight.gd','--',marker],report=root/'captures/cliff-flight-validation.json')
        required.add('geology')
        run.stage('geology',[sys.executable,'tools/verify_geology_assets.py'],report=root/'captures/geology-asset-validation.json')
        run.assert_inputs()
        overlap=validate_section_overlap(root,root/'captures/round-10a-section-overlap-check.json',run.inputs)
        overlap['run_id']=run.run_id
        write_json(run.directory/'section-overlap-binding.json',overlap);run.bind(run.directory/'section-overlap-binding.json')
        for source in ['round-10a-section-overlap-check.json','check_section_surface_overlaps.py']:
            target=run.directory/source;shutil.copy2(root/'captures'/source,target);run.bind(target)
            if source.endswith('.json'):require(sha256(target)==overlap['report_sha256'],'Section overlap report changed while copying')
        run.assert_inputs()
        require({stage['name'] for stage in run.manifest['stages']}==required and all(s['passed'] for s in run.manifest['stages']),'Incomplete scoped check set')
        for path,record in run.manifest['artifacts'].items():require(sha256(run.directory/path)==record['sha256'],'Changed evidence: '+path)
        run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
        print('Scoped cliff checks passed; visual and release acceptance remain unproven. '+str(run.directory),flush=True)
    except Exception as error:
        run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
