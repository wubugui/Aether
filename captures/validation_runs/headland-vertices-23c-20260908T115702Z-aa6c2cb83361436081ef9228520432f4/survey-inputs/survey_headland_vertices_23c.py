from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json
def main():
    root=Path(__file__).resolve().parents[1]
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'headland-vertices-23c',False,True);run.manifest.update(scope='Read-only original ground and SeaCollision-excluded terrain bed at each authored Blender layout vertex. Dummy audio, native GPU physics.',expected_counts={})
        try:
            frozen=run.directory/'survey-inputs';frozen.mkdir()
            for path in [Path(__file__),root/'captures/survey_headland_vertices_23c.gd',root/'captures/headland_layout_23c/layout.json',root/'blender/layout_headland_23c.py',root/'reviews/reference-view-1342-progress-22g.json',root/'captures/validation_runs/headland-vertices-23b-20260908T114829Z-7a10446678fb4e16ba7809839478ec44/survey/vertex-survey.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            run.inputs=snapshot_inputs(root,imported=True);write_json(run.directory/'inputs.json',{'run_id':run.run_id,'files':run.inputs});run.bind(run.directory/'inputs.json')
            out=run.directory/'survey';out.mkdir();report=out/'vertex-survey.json'
            run.stage('native-vertex-ground',[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'survey_headland_vertices_23c.gd','--quit-after','900','--','--reuse='+str(frozen/'vertex-survey.json'),'--layout='+str(frozen/'layout.json'),'--reference='+str(frozen/'reference-view-1342-progress-22g.json'),'--output='+str(report),'--validation-run='+run.run_id],outputs=[report])
            data=read_json(report);require(data['run_id']==run.run_id and len(data['samples'])==len(read_json(frozen/'layout.json')['vertices']),'Incomplete vertex survey')
            require(data['layout_sha256']==sha256(frozen/'layout.json'),'Layout changed')
            run.assert_inputs()
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('HEADLAND VERTICES READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise
if __name__=='__main__':main()
