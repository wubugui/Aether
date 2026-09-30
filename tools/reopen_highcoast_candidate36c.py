from pathlib import Path
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,utc_now

R=Path(__file__).resolve().parents[1]
with exclusive_lock(R/'captures/.validation-pipeline.lock'):
    run=ValidationRun(R,'highcoast-reopen36c',False,True)
    run.manifest['scope']='Resource-path repair and fresh native candidate World/Game + bounded physical flight; no geometry regeneration or repeat36b12view suite.'
    try:
        for p in (R/'captures/candidate_highcoast36c').iterdir():
            if p.is_file():run.bind(p)
        run.bind(R/'tools/check_highcoast_candidate_36c.gd')
        run.bind(Path(__file__))
        folder=run.directory/'images';folder.mkdir(exist_ok=True)
        run.stage('native-candidate-reopen',[R/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',R,'--audio-driver','Dummy','--script',R/'tools/check_highcoast_candidate_36c.gd','--quit-after','1600','--','--output-dir='+str(folder)],image=folder/'candidate-flight.png',outputs=[folder/'candidate-start.png',folder/'candidate-reopen.json'])
        data=read_json(folder/'candidate-reopen.json')
        require(data['passed'] and data['scatter_total']==54800 and len(data['tile_checks'])==14,'Candidate checks incomplete')
        run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
        print('36c REOPEN READY '+str(run.directory),flush=True)
    except Exception as e:
        run.manifest.update(status='failed',passed=False,error=str(e),completed_utc=utc_now());run.save();raise
