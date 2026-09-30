"""Native camera projection and original ground, before local coastal sculpting."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json,validate_png
def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'headland-survey-23a',False,True);run.manifest.update(scope='Original ground and native projection for a proposed near-right rocky headland. Dummy audio; real GPU. No geometry changes or original-map inference.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_headland_23a.gd',root/'reviews/reference-view-1342-progress-22g.json',root/'ref/1342.png']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            out=run.directory/'survey';out.mkdir();report=out/'headland.json';picture=out/'reference-before.png'
            run.stage('native-headland-projection',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'survey_headland_23a.gd','--quit-after','900','--','--survey='+str(frozen/'reference-view-1342-progress-22g.json'),'--output-dir='+str(out),'--validation-run='+run.run_id],outputs=[report,picture])
            data=read_json(report);require(data['run_id']==run.run_id and len(data['anchors'])==21 and len(data['grid'])>800,'Incomplete headland survey');validate_png(picture)
            require(max(p['reprojection_error_px'] for p in data['anchors'])<.01,'Projection identity mismatch')
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('HEADLAND SURVEY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
