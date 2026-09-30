from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'tools/render_harbor_assembly_22a.py').read_text(encoding='utf-8')
source=source.replace("run=ValidationRun(root,'harbor-assembly-22a'","run=ValidationRun(root,'harbor-assembly-22e'")
source=source.replace("root/'captures/harbor_kit_study_22a'","root/'captures/harbor_kit_study_22b'").replace("root/'reviews/round-22a-harbor-native-check.json'","root/'reviews/round-22b-harbor-native-check.json'")
source=source.replace('harbor_assembly_22a.gd','harbor_assembly_22e.gd')
source=source.replace('Six new detailed Blender harbor modules,23 surveyed native houses and4 piers in the same20l island/21c night world. Six actual GPU views. Temporary scene, no full reference, land-route, seabed or production acceptance.','Four terrain-surveyed Blender stone approaches with landings, repaired22b dock joints and seaward boat repositioning in the same20l/21c world. Actual path top/base collision rays and boat vertex ground probes. Temporary, no full reference, movement, seabed or production acceptance.')
anchor="            survey=root/'captures/validation_runs/harbor-sites-22a"
insertion='''            path_source=root/'captures/harbor_paths_study_22e'
            path_gate=root/'reviews/round-22e-harbor-paths-native-check.json'
            require(read_json(path_gate)['passed'],'Stone approach native source failed')
            path_frozen=frozen/'stone-approaches';path_frozen.mkdir()
            for path in path_source.iterdir():
                if path.is_file():shutil.copy2(path,path_frozen/path.name);run.bind(path_frozen/path.name)
            shutil.copy2(path_gate,path_frozen/path_gate.name);run.bind(path_frozen/path_gate.name)
            for item in read_json(path_gate)['assets']:
                require(sha256(path_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(path_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Stone approach source identity changed')
            runtime=root/'captures/harbor_path_runtime_22e.gd';shutil.copy2(runtime,frozen/runtime.name);run.bind(frozen/runtime.name)
'''
assert source.count(anchor)==1;source=source.replace(anchor,insertion+anchor)
anchor='\\tvar environment_report:Dictionary=adapter.configure(game,region,directory.path_join("environment"),environment_mode=="night")'
extra='''\\tawait physics_frame;await physics_frame;await physics_frame
\\tharbor_report["stone_paths"]["runtime_checks"]=harbor_adapter.path_adapter.validate()
\\tharbor_report["boat_ground_samples"]=harbor_adapter.path_adapter.validate_boats(harbor_adapter.root)'''
assert source.count(anchor)==1;source=source.replace(anchor,anchor+'\n'+extra)
source=source.replace('"dock-front","dock-back","boat-close":pass','"dock-front","dock-back","boat-close","path-approach","paths-overview","path-door","path0-curve":pass')
old="views=[('day-reference','reference-coast-near','day'),('night-reference','reference-coast-near','night'),('dock-front','dock-front','day'),('dock-back','dock-back','day'),('boat-close','boat-close','day'),('night-dock','dock-front','night')]"
new="views=[('path-approach','path-approach','day'),('path-door','path-door','day'),('paths-overview','paths-overview','day'),('path0-curve','path0-curve','day'),('dock-repair','dock-front','day'),('night-path','paths-overview','night'),('night-reference','reference-coast-near','night')]"
assert source.count(old)==1;source=source.replace(old,new)
source=source.replace("len(harbor['lights'])==39","len(harbor['lights'])==39+len(harbor['stone_paths']['lamp_sites'])")
anchor="                require(all(point['gap_m']<0 for house in harbor['house_footings'] for point in house['samples']),'Positive sampled harbor foundation gap')"
extra='''
                paths=harbor['stone_paths'];require(len(paths['assets'])==4 and paths['runtime_checks']['passed'],'Stone approach runtime contact failure')
                require(len(harbor['boat_ground_samples'])==4,'Missing original-ground probes for4 boats')
                bad=[p for boat in harbor['boat_ground_samples'] for p in boat['samples'] if p['placement']=='candidate_22e' and p['clearance_m'] is not None and p['clearance_m']<-.02]
                require(not bad,'Known sampled boat-ground intersection in new placement')'''
assert source.count(anchor)==1;source=source.replace(anchor,anchor+extra)
target=root/'tools/render_harbor_assembly_22e.py';assert not target.exists();target.write_text(source,encoding='utf-8')
