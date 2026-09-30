"""Validate the already-installed lighthouse; preserve both failed predecessor runs."""
from pathlib import Path
import shutil
from validation_manifest import (ValidationRun,exclusive_lock,input_diff,read_json,require,
    sha256,snapshot_inputs,utc_now,write_json)

def main():
    root=Path(__file__).resolve().parents[1]
    installed=root/'captures/validation_runs/19h-native-lighthouse-repair-20260908T082039Z-7c31371c56954044b4576030f27feea3'
    manifest=read_json(installed/'manifest.json')
    require(manifest['status']=='failed' and manifest['stages'][0]['name']=='derived-install' and manifest['stages'][0]['passed'],'Unexpected predecessor state')
    expected=read_json(installed/'inputs.json')['files']
    require(not input_diff(expected,snapshot_inputs(root,imported=True)),'Installed production changed since resource save')
    report=read_json(installed/'reports/derived-install.json')
    require(report['passed'] and report['combined_surfaces']==24 and report['collision_triangles']==3988,'Incomplete derived resources')
    engine=root/'.tools/godot/Godot_v4.5.1-stable_win64.exe'
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'19h-native-lighthouse-final',False,True)
        run.manifest.update(scope='Read-only validation of 19h installed architecture: all saved mesh/collision vertices, PBR alpha/material ownership, both placements, 32 contact rays, seven local GPU captures plus opening and 36 gameplay checks. Preserve failed tangent-array and overly narrow alpha-mode checks. No all-reference visual claim.',
            expected_counts={'game-test':36},installed_from=str(installed),production_mutations_in_this_run=0)
        try:
            for name,record in manifest['artifacts'].items():
                path=installed/name;require(sha256(path)==record['sha256'],'Predecessor evidence changed: '+name)
                dest=run.directory/'installed-evidence'/name;dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,dest);run.bind(dest)
            shutil.copy2(installed/'manifest.json',run.directory/'installed-evidence/manifest.json');run.bind(run.directory/'installed-evidence/manifest.json')
            frozen=run.directory/'validation-scripts';frozen.mkdir()
            for path in [Path(__file__),root/'captures/native_lighthouse_19.gd',root/'captures/capture_native_lighthouse_19.gd',
                         root/'captures/inspect_native_lighthouse_materials_19.gd',root/'captures/lighthouse-19h-native-material-diagnostic.stdout.log',root/'captures/lighthouse-19h-native-material-diagnostic.stderr.log']:
                dest=frozen/path.name;shutil.copy2(path,dest);run.bind(dest)
            run.inputs=expected
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':expected})
            run.bind(run.directory/'inputs.json');run.manifest['input_count']=len(expected);run.save()
            marker='--validation-run='+run.run_id
            output=run.directory/'reports/native-check.json'
            run.stage('native-check',[engine,'--path',root,'--script',frozen/'native_lighthouse_19.gd','--quit-after','600','--','--mode=check','--output='+str(output),marker],outputs=[output])
            result=read_json(output)
            require(result['passed'] and result['run_id']==run.run_id and result['collision_triangles']==3988,'Native identity failed')
            require(result['model_sha256']==expected['res://assets/models/lighthouse.glb']['sha256'],'Wrong model')
            require(result['world_sha256']==expected['res://scenes/world/World.tscn']['sha256'],'Wrong world')
            require(len(result['instances'])==2 and all(len(i['collision_contacts'])==16 and len(i['materials'])==24 for i in result['instances']),'Missing native contacts/materials')
            for site,views in [('harbor',('front','back','gallery','context','door')),('remote',('front','door'))]:
                for view in views:
                    output=run.directory/'images'/(site+'-'+view+'.png')
                    run.stage('capture-'+site+'-'+view,[engine,'--path',root,'--script',frozen/'capture_native_lighthouse_19.gd','--','--site='+site,'--view='+view,'--output='+str(output),marker],image=output)
            output=run.directory/'images/opening.png'
            run.stage('capture-opening',[engine,'--path',root,'--','--capture','--view=opening','--output='+str(output),marker],image=output)
            run.stage('game-test',[engine,'--path',root,'--','--game-test',marker],report=root/'captures/game-validation.json')
            run.assert_inputs()
            for name,record in run.manifest['artifacts'].items():require(sha256(run.directory/name)==record['sha256'],'Changed evidence')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('NATIVE LIGHTHOUSE FINAL VALIDATION PASS '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
