from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'village-grid-24a',False,True);run.manifest.update(scope='Actual23g headland collision height grid for nine-house shared courtyards and short stair connections. Read-only, original World retained.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_village_grid_24a.gd',root/'captures/headland_study_23g/mainland_headland.glb',root/'captures/headland_study_23g/layout.json',root/'reviews/round-23g-headland-independent-audit.json',root/'reviews/reference-view-1342-progress-23g.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            out=run.directory/'survey';out.mkdir();report=out/'grid.json'
            run.stage('native-village-grid',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'survey_village_grid_24a.gd','--quit-after','900','--','--source='+str(frozen),'--output='+str(report),'--validation-run='+run.run_id],outputs=[report])
            data=read_json(report);require(data['run_id']==run.run_id and len(data['grids'])==2,'Missing grid data');require(data['headland_glb_sha256']==sha256(frozen/'mainland_headland.glb'),'Headland changed')
            require([len(g['samples']) for g in data['grids']]==[81*91,76*86],'Grid count mismatch')
            run.assert_inputs();run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('VILLAGE GRID READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
