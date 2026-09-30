"""Native coast survey for the next unified lighthouse-island scene composition."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json,validate_png

def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'20a-native-coast-survey',False,True)
        run.manifest.update(scope='Read-only authored northwest coast survey for actual scene placement. Not new island geometry or reference completion.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_lantern_coast_20.gd',root/'ref/1126.png',root/'ref/1342.png']:
                dest=frozen/path.name;shutil.copy2(path,dest);run.bind(dest)
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs});run.bind(run.directory/'inputs.json')
            output=run.directory/'survey';output.mkdir()
            report=output/'survey.json';images=[output/'topdown.png',output/'coast-oblique.png']
            run.stage('native-coast-survey',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--script',frozen/'survey_lantern_coast_20.gd','--quit-after','600','--','--output-dir='+str(output),'--validation-run='+run.run_id],outputs=[report]+images)
            data=read_json(report)
            require(data['run_id']==run.run_id and len(data['samples'])==2565,'Incomplete survey')
            require(data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'World mismatch')
            require(data['lighthouse_model_sha256']==run.inputs['res://assets/models/lighthouse.glb']['sha256'],'Lighthouse mismatch')
            for path in images:validate_png(path)
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Changed survey evidence')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('NATIVE COAST SURVEY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
