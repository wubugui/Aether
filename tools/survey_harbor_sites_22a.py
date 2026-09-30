"""Actual local shoreline and building-footprint survey before harbor assembly."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json,validate_png
def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'harbor-sites-22a',False,True)
        run.manifest.update(scope='Native shore transects and proposed building/pier foundation survey. No production changes.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_harbor_sites_22a.gd',root/'reviews/round-22a-port-site-independent-audit.json',root/'ref/1342.png',root/'ref/1135.png']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            output=run.directory/'survey';output.mkdir();report=output/'survey.json';picture=output/'harbor-before.png'
            run.stage('native-port-sites',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--script',frozen/'survey_harbor_sites_22a.gd','--quit-after','900','--','--output-dir='+str(output),'--validation-run='+run.run_id],outputs=[report,picture])
            data=read_json(report);require(data['run_id']==run.run_id and len(data['shore_transects'])==16 and len(data['piers'])==4,'Incomplete survey')
            require(data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'World changed');validate_png(picture)
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('HARBOR SURVEY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
