"""Freeze local Blender coastal assets and render them in the continuous native world."""
from pathlib import Path
import argparse,shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('label',choices=['20c','20d','20e','20f','20g','20h','20i']);args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    source=root/'captures'/('lantern_islands_study_'+args.label)
    gate=root/'reviews'/('round-'+args.label+'-coast-native-check.json')
    require(read_json(gate)['passed'],'Candidate native gate failed')
    if args.label=='20h':require(read_json(root/'reviews/round-20h-roof-laps.json')['passed'],'Roof course clearance gate failed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'lantern-islands-'+args.label,False,True)
        run.manifest.update(scope='Three Blender islands, three reef variants and keeper house, with native 19h lighthouses at proposed sea positions in one continuous world. Six real GPU views. Temporary assembly, no production changes or full scene/weather acceptance.',expected_counts={})
        try:
            frozen=run.directory/'study-inputs';frozen.mkdir()
            for path in sorted(source.iterdir()):
                if path.is_file():shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            for asset in read_json(gate)['assets']:
                require(asset['source_sha256']==sha256(frozen/(asset['asset']+'.blend')),'Native source changed')
            for asset in read_json(source/'model-report.json')['assets']:
                require(asset['source_sha256']==sha256(frozen/(asset['name']+'.blend')) and asset['glb_sha256']==sha256(frozen/(asset['name']+'.glb')),'Candidate export identity changed')
            for path in [gate,Path(__file__),root/'captures/preview_lantern_islands_20.gd',root/'ref/1126.png',root/'ref/1342.png',root/'ref/1218.png']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            if args.label=='20h':
                for path in [root/'reviews/round-20h-roof-laps.json',root/'captures/check_keeper_roof_laps.py']:
                    shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
                run.manifest['scope']='Keeper roof lap repair only, with all six 20g landforms byte-identical. Four actual GPU views: house front/back, island-chain context and C building site. Temporary assembly; no full scene acceptance.'
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs});run.bind(run.directory/'inputs.json')
            views=['archipelago','island-front','island-back','shoreline','house-front','house-back']
            if args.label=='20g':views+=['c-site']
            if args.label=='20h':views=['house-front','house-back','archipelago','c-site']
            if args.label=='20i':
                views=['archipelago','island-front','island-back','shoreline','paths','b-site','c-site']
                run.manifest['scope']='Three rebuilt coastal landforms with actual raised bare-rock shoulders, inclined cliff bands and terrain-fitted solid paths. Seven real GPU views. Keeper house/reef assets retained from20h; temporary assembly, no full scene acceptance.'
            for view in views:
                output=run.directory/'images'/(view+'.png');report=Path(str(output)+'.json')
                run.stage('capture-'+view,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--script',frozen/'preview_lantern_islands_20.gd','--quit-after','900','--','--label='+args.label,'--study-dir='+str(frozen),'--view='+view,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                data=read_json(report)
                require(data['run_id']==run.run_id and data['view']==view,'Capture identity mismatch')
                require(data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'Different world')
                require(data['lighthouse_sha256']==run.inputs['res://assets/models/lighthouse.glb']['sha256'],'Different lighthouse')
                require(len(data['footing_samples'])==7,'Expected 3 lighthouse and 4 house footprints')
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('LANTERN ISLAND STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
