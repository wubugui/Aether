from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,utc_now
R=Path(__file__).resolve().parents[1]
with exclusive_lock(R/'captures/.validation-pipeline.lock'):
    run=ValidationRun(R,'crownreach37c',False,True)
    try:
        for p in [Path(__file__),R/'tools/render_crownreach37c.gd',R/'captures/crownreach_study_37c/castle.blend',R/'captures/crownreach_study_37c/castle.glb',R/'captures/crownreach_study_37c/model-report.json',R/'captures/crownreach_study_37c/builder.py',R/'ref/1343.png']:
            dest=run.directory/p.name;shutil.copy2(p,dest);run.bind(dest)
        folder=run.directory/'images';folder.mkdir()
        run.stage('castle-native-gpu',[R/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',R,'--audio-driver','Dummy','--script',R/'tools/render_crownreach37c.gd','--quit-after','800','--','--output-dir='+str(folder)],image=folder/'castle-front.png',outputs=[folder/(s+'.png') for s in ['gate-low','flight-end']]+[folder/'castle37c.json',folder/'castle37c.tscn',folder/'World37c.tscn',folder/'Game37c.tscn'])
        run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('37C NATIVE AND FLIGHT '+str(run.directory),flush=True)
    except Exception as e:
        run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
