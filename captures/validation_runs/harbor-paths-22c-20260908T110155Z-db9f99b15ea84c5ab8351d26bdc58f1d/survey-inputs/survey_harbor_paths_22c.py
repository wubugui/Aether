"""Capture only the new pier aprons and land-route cross sections."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json,validate_png
def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'harbor-paths-22c',False,True);run.manifest.update(scope='Read-only five-wide sections for4 curved, continuously aligned pier-to-door approaches.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_harbor_paths_22c.gd']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            prior=root/'captures/validation_runs/harbor-sites-22a-20260908T103705Z-af34540b52054103be479e592bea4f7d/survey/survey.json'
            shutil.copy2(prior,frozen/'sites.json');run.bind(frozen/'sites.json')
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            out=run.directory/'survey';out.mkdir();report=out/'paths.json';picture=out/'paths-before.png'
            run.stage('native-route-transects',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--script',frozen/'survey_harbor_paths_22c.gd','--quit-after','900','--','--survey='+str(frozen/'sites.json'),'--output-dir='+str(out),'--validation-run='+run.run_id],outputs=[report,picture])
            data=read_json(report);require(data['run_id']==run.run_id and len(data['paths'])==4,'Incomplete new route survey');validate_png(picture)
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('HARBOR PATH SURVEY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
