from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,utc_now
R=Path(__file__).resolve().parents[1]
with exclusive_lock(R/'captures/.validation-pipeline.lock'):
    run=ValidationRun(R,'crownreach37-intake',False,True)
    try:
        for p in [Path(__file__),R/'tools/inspect_crownreach37.gd',R/'ref/1343.png',R/'scenes/game.tscn',R/'captures/candidate_highcoast36c/World36c.tscn',R/'captures/candidate_highcoast36c/Game36c.tscn']:
            dest=run.directory/p.name;shutil.copy2(p,dest);run.bind(dest)
        folder=run.directory/'images';folder.mkdir()
        run.stage('central-daylight-intake',[R/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',R,'--audio-driver','Dummy','--script',R/'tools/inspect_crownreach37.gd','--quit-after','600','--','--output-dir='+str(folder)],image=folder/'opening.png',outputs=[folder/'castle-front.png',folder/'castle-back.png',folder/'castle-river.png',folder/'intake.json'])
        run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
        print('37 INTAKE '+str(run.directory),flush=True)
    except Exception as e:
        run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
