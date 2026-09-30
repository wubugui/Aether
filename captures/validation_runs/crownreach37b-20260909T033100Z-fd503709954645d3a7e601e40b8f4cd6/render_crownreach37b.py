from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,utc_now
R=Path(__file__).resolve().parents[1]
with exclusive_lock(R/'captures/.validation-pipeline.lock'):
    run=ValidationRun(R,'crownreach37b',False,True)
    try:
        for p in [Path(__file__),R/'tools/render_crownreach37b.gd',R/'captures/crownreach_study_37b/castle.blend',R/'captures/crownreach_study_37b/castle.glb',R/'captures/crownreach_study_37b/model-report.json',R/'captures/crownreach_study_37b/builder.py',R/'ref/1343.png']:
            dest=run.directory/p.name;shutil.copy2(p,dest);run.bind(dest)
        folder=run.directory/'images';folder.mkdir()
        run.stage('castle-native-gpu',[R/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',R,'--audio-driver','Dummy','--script',R/'tools/render_crownreach37b.gd','--quit-after','800','--','--output-dir='+str(folder)],image=folder/'opening.png',outputs=[folder/(s+'.png') for s in ['castle-front','castle-back','castle-river','gate-low','orbit-end']]+[folder/'castle37b.json',folder/'castle37b.tscn',folder/'World37b.tscn',folder/'Game37b.tscn'])
        run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save();print('37A GPU '+str(run.directory),flush=True)
    except Exception as e:
        run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
