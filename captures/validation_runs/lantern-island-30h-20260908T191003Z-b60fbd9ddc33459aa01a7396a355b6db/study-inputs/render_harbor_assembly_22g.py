"""Freeze20l Blender terrain and21c material study; capture actual day/night GPU views."""
from pathlib import Path
import shutil
from validation_manifest import ValidationRun,exclusive_lock,read_json,require,sha256,snapshot_inputs,utc_now,write_json

def main():
    root=Path(__file__).resolve().parents[1]
    source=root/'captures/lantern_islands_study_20l'
    gate=root/'reviews/round-20l-coast-native-check.json'
    require(read_json(gate)['passed'],'Native source gate failed')
    with exclusive_lock(root/'captures/.validation-pipeline.lock'):
        run=ValidationRun(root,'harbor-assembly-22g',False,True)
        run.manifest.update(scope='Four terrain-surveyed Blender stone approaches with landings, repaired22b dock joints and seaward boat repositioning in the same20l/21c world. Actual path top/base collision rays and boat vertex ground probes. Boat center moved4.0m seaward relative22a after measured grounding. Visual-only run uses Dummy audio after prior WASAPI device invalidation; actual OpenGL GPU retained. Temporary, no audio, full reference, movement, seabed or production acceptance.',expected_counts={})
        try:
            frozen=run.directory/'study-inputs';frozen.mkdir()
            for path in source.iterdir():
                if path.is_file():shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            for item in read_json(gate)['assets']:require(sha256(frozen/(item['asset']+'.blend'))==item['source_sha256'],'Source gate identity changed')
            for item in read_json(source/'model-report.json')['assets']:require(sha256(frozen/(item['name']+'.glb'))==item['glb_sha256'],'Export identity changed')
            environment=frozen/'environment';environment.mkdir()
            for path in (root/'captures/coast_environment_study_21c').iterdir():
                if path.is_file():shutil.copy2(path,environment/path.name);run.bind(environment/path.name)
            sky_source=root/'captures/coastal_sky_assets_21b'
            sky_gate=root/'reviews/round-21b-sky-native-check.json'
            require(read_json(sky_gate)['passed'],'Sky native gate failed')
            sky_frozen=environment/'sky-assets';sky_frozen.mkdir()
            for path in sky_source.iterdir():
                if path.is_file():shutil.copy2(path,sky_frozen/path.name);run.bind(sky_frozen/path.name)
            shutil.copy2(sky_gate,sky_frozen/sky_gate.name);run.bind(sky_frozen/sky_gate.name)
            for item in read_json(sky_gate)['assets']:
                require(sha256(sky_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(sky_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Sky source/export identity changed')
            harbor_source=root/'captures/harbor_kit_study_22b'
            harbor_gate=root/'reviews/round-22b-harbor-native-check.json'
            require(read_json(harbor_gate)['passed'],'Harbor native source failed')
            harbor_frozen=frozen/'harbor-kit';harbor_frozen.mkdir()
            for path in harbor_source.iterdir():
                if path.is_file():shutil.copy2(path,harbor_frozen/path.name);run.bind(harbor_frozen/path.name)
            shutil.copy2(harbor_gate,harbor_frozen/harbor_gate.name);run.bind(harbor_frozen/harbor_gate.name)
            for item in read_json(harbor_gate)['assets']:
                require(sha256(harbor_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(harbor_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Harbor source identity changed')
            path_source=root/'captures/harbor_paths_study_22f'
            path_gate=root/'reviews/round-22f-harbor-paths-native-check.json'
            require(read_json(path_gate)['passed'],'Stone approach native source failed')
            path_frozen=frozen/'stone-approaches';path_frozen.mkdir()
            for path in path_source.iterdir():
                if path.is_file():shutil.copy2(path,path_frozen/path.name);run.bind(path_frozen/path.name)
            shutil.copy2(path_gate,path_frozen/path_gate.name);run.bind(path_frozen/path_gate.name)
            for item in read_json(path_gate)['assets']:
                require(sha256(path_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(path_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Stone approach source identity changed')
            runtime=root/'captures/harbor_path_runtime_22g.gd';shutil.copy2(runtime,frozen/runtime.name);run.bind(frozen/runtime.name)
            survey=root/'captures/validation_runs/harbor-sites-22a-20260908T103705Z-af34540b52054103be479e592bea4f7d/survey/survey.json'
            shutil.copy2(survey,frozen/'harbor-survey.json');run.bind(frozen/'harbor-survey.json')
            for path in [root/'captures/harbor_assembly_22g.gd',root/'ref/1135.png',root/'reviews/round-22a-port-site-independent-audit.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            for path in [gate,Path(__file__),root/'captures/coast_environment_21c.gd',root/'captures/environment-sources-runtime.log',root/'captures/inspect_environment_sources.gd',root/'ref/1342.png',root/'reviews/round-20l-path-independent-audit.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
            preview=(root/'captures/preview_lantern_islands_20.gd').read_text()
            anchor='\tfor i in range(40):await process_frame'
            insertion='''\tvar environment_mode:="day"
\tfor arg in OS.get_cmdline_user_args():
\t\tif arg.begins_with("--environment="):environment_mode=arg.trim_prefix("--environment=")
\tvar harbor_adapter=load(directory.path_join("harbor_assembly_22g.gd")).new()
\tvar harbor_report:Dictionary=harbor_adapter.configure(game,directory,environment_mode=="night",camera,view)
\tvar adapter=load(directory.path_join("coast_environment_21c.gd")).new()
\tvar environment_report:Dictionary=adapter.configure(game,region,directory.path_join("environment"),environment_mode=="night")
\tawait physics_frame;await physics_frame;await physics_frame
\tharbor_report["stone_paths"]["runtime_checks"]=harbor_adapter.path_adapter.validate()
\tharbor_report["boat_ground_samples"]=harbor_adapter.path_adapter.validate_boats(harbor_adapter.root)
'''
            require(preview.count(anchor)==1,'Preview injection anchor changed')
            preview=preview.replace('Actual temporary 3D geometry in existing world daytime; not night/fog/whole reference acceptance.','Actual temporary 3D geometry in existing world; lighting mode recorded in environment_study, no full reference acceptance.')
            preview=preview.replace(anchor,insertion+anchor).replace('report["site_checks"]=site_checks','report["site_checks"]=site_checks\n\treport["environment_study"]=environment_report')
            preview=preview.replace('\t\t_:assert(false)','\t\t"dock-front","dock-back","boat-close","path-approach","paths-overview","path-door","path0-curve":pass\n\t\t_:assert(false)')
            preview=preview.replace('report["environment_study"]=environment_report','report["environment_study"]=environment_report\n\treport["harbor_study"]=harbor_report')
            (frozen/'preview.gd').write_text(preview);run.bind(frozen/'preview.gd')
            run.inputs=snapshot_inputs(root,imported=True)
            write_json(run.directory/'inputs.json',{'run_id':run.run_id,'frozen_utc':utc_now(),'files':run.inputs});run.bind(run.directory/'inputs.json')
            views=[('path-approach','path-approach','day'),('path-door','path-door','day'),('paths-overview','paths-overview','day'),('path0-curve','path0-curve','day'),('dock-repair','dock-front','day'),('night-path','paths-overview','night'),('night-reference','reference-coast-near','night')]
            for name,view,mode in views:
                output=run.directory/'images'/(name+'.png');report=Path(str(output)+'.json')
                run.stage(name,[root/'.tools/godot/Godot_v4.5.1-stable_win64.exe','--path',root,'--audio-driver','Dummy','--script',frozen/'preview.gd','--quit-after','900','--','--label=20l','--study-dir='+str(frozen),'--view='+view,'--environment='+mode,'--output='+str(output),'--validation-run='+run.run_id],image=output,outputs=[report])
                data=read_json(report);env=data['environment_study']
                require(data['run_id']==run.run_id and data['view']==view,'Capture identity mismatch')
                require(len(data['footing_samples'])==9 and len(data['site_checks'])==1,'Missing buildings or site evidence')
                require(data['world_sha256']==run.inputs['res://scenes/world/World.tscn']['sha256'],'World changed')
                require(env['night']==(mode=='night') and len(env['material_bindings'])>=5,'Environment not applied')
                require(len(env['native_sky_assets'])==(8 if mode=='night' else 7),'Native sky geometry missing')
                if mode=='night':require(env['ambient_source']==2 and len(env['local_light_records'])==4,'Color ambient or lamp records missing')
                harbor=data['harbor_study']
                require(len(harbor['house_footings'])==23 and len(harbor['pier_entries'])==4 and len(harbor['lights'])==39+len(harbor['stone_paths']['lamp_sites']),'Incomplete harbor assembly')
                require(all(point['gap_m']<0 for house in harbor['house_footings'] for point in house['samples']),'Positive sampled harbor foundation gap')
                paths=harbor['stone_paths'];require(len(paths['assets'])==4 and paths['runtime_checks']['passed'],'Stone approach runtime contact failure')
                require(len(harbor['boat_ground_samples'])==4,'Missing original-ground probes for4 boats')
                bad=[p for boat in harbor['boat_ground_samples'] for p in boat['samples'] if p['placement']=='candidate_22g' and p['clearance_m'] is not None and p['clearance_m']<-.02]
                require(not bad,'Known sampled boat-ground intersection in new placement')
            run.assert_inputs()
            for path,item in run.manifest['artifacts'].items():require(sha256(run.directory/path)==item['sha256'],'Evidence changed')
            run.manifest.update(status='passed',passed=True,completed_utc=utc_now());run.save()
            print('HARBOR ASSEMBLY STUDY READY '+str(run.directory),flush=True)
        except Exception as error:
            run.manifest.update(status='failed',passed=False,error=str(error),completed_utc=utc_now());run.save();raise

if __name__=='__main__':main()
