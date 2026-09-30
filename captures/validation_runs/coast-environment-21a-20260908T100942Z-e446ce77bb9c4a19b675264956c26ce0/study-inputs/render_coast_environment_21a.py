"""Freeze20l Blender terrain and21a material study; capture actual day/night GPU views."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    root=Path(__file__).resolve().parents[1]
    source=root/'captures/lantern_islands_study_20l'
    gate=root/'reviews/round-20l-coast-native-check.json'
    require(read_json(gate)['passed'],'Native source gate failed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'coast-environment-21a',False,True)
        run.manifest.update(scope='Actual temporary20l native Blender island geometry with21a lighting/material study. Day paths and reference view, same reference at night and a reverse night view. Not production integration, full weather or reference acceptance.',expected_counts={})
        try:
            frozen=run.directory/'study-inputs';frozen.mkdir()
            for path in source.iterdir():
                if path.is_file():shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            for item in read_json(gate)['assets']:require(sha256(frozen/(item['asset']+'.blend'))==item['source_sha256'],'Source gate identity changed')
            for item in read_json(source/'model-report.json')['assets']:require(sha256(frozen/(item['name']+'.glb'))==item['glb_sha256'],'Export identity changed')
            environment=frozen/'environment';environment.mkdir()
            for path in (root/'captures/coast_environment_study_21a').iterdir():
                if path.is_file():shutil.copy2(path,environment/path.name);run.bind(environment/path.name)
            for path in [gate,Path(__file__),root/'captures/coast_environment_21a.gd',root/'ref/1342.png',root/'reviews/round-20l-path-independent-audit.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            preview=(root/'captures/preview_lantern_islands_20.gd').read_text()
            anchor='\tfor i in range(40):await process_frame'
            insertion='''\tvar environment_mode:="day"
\tfor arg in OS.get_cmdline_user_args():
\t\tif arg.begins_with("--environment="):environment_mode=arg.trim_prefix("--environment=")
\tvar adapter=load(directory.path_join("coast_environment_21a.gd")).new()
\tvar environment_report:Dictionary=adapter.configure(game,region,directory.path_join("environment"),environment_mode=="night")
'''
            require(preview.count(anchor)==1,'Preview injection anchor changed')
            preview=preview.replace(anchor,insertion+anchor).replace('report["site_checks"]=site_checks','report["site_checks"]=site_checks\n\treport["environment_study"]=environment_report')
            (frozen/'preview.gd').write_text(preview);run.bind(frozen/'preview.gd')
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs});run.bind(run.directory/'inputs.json')
            views=[('day-paths','paths','day'),('day-reference','reference-coast-near','day'),('night-reference','reference-coast-near','night'),('night-back','island-back','night')]
            for name,view,mode in views:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--script',frozen/'preview.gd','--quit-after','900','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                data=read_json(report);env=data['environment_study']
                require(data['run_id']==run.run_id and data['view']==view,'Capture identity mismatch')
                require(len(data['footing_samples'])==9 and len(data['site_checks'])==1,'Missing buildings or site evidence')
                require(data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'World changed')
                require(env['night']==(mode=='night') and len(env['material_bindings'])>=5,'Environment not applied')
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('COAST ENVIRONMENT STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
