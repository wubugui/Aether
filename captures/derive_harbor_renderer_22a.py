from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'tools/render_harbor_assembly_22a.py';assert not p.exists()
s=(root/'tools/render_coast_environment_21c.py').read_text(encoding='utf-8')
s=s.replace("run=ValidationRun(root,'coast-environment-21c'","run=ValidationRun(root,'harbor-assembly-22a'")
start=s.index("        run.manifest.update(scope=");end=s.index('\n        try:',start)
s=s[:start]+"        run.manifest.update(scope='Six new detailed Blender harbor modules,23 surveyed native houses and4 piers in the same20l island/21c night world. Six actual GPU views. Temporary scene, no full reference, land-route, seabed or production acceptance.',expected_counts={})"+s[end:]
anchor="            for path in [gate,Path(__file__)";at=s.index(anchor)
insert='''            harbor_source=root/'captures/harbor_kit_study_22a'
            harbor_gate=root/'reviews/round-22a-harbor-native-check.json'
            require(read_json(harbor_gate)['passed'],'Harbor native source failed')
            harbor_frozen=frozen/'harbor-kit';harbor_frozen.mkdir()
            for path in harbor_source.iterdir():
                if path.is_file():shutil.copy2(path,harbor_frozen/path.name);run.bind(harbor_frozen/path.name)
            shutil.copy2(harbor_gate,harbor_frozen/harbor_gate.name);run.bind(harbor_frozen/harbor_gate.name)
            for item in read_json(harbor_gate)['assets']:
                require(sha256(harbor_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(harbor_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Harbor source identity changed')
            survey=root/'captures/validation_runs/harbor-sites-22a-20260908T103705Z-af34540b52054103be479e592bea4f7d/survey/survey.json'
            shutil.copy2(survey,frozen/'harbor-survey.json');run.bind(frozen/'harbor-survey.json')
            for path in [root/'captures/harbor_assembly_22a.gd',root/'ref/1135.png',root/'reviews/round-22a-port-site-independent-audit.json']:
                shutil.copy2(path,frozen/path.name);run.bind(frozen/path.name)
'''
s=s[:at]+insert+s[at:]
anchor='\\tvar adapter=load(directory.path_join("coast_environment_21c.gd")).new()'
assert anchor in s
s=s.replace(anchor,'''\\tvar harbor_adapter=load(directory.path_join("harbor_assembly_22a.gd")).new()
\\tvar harbor_report:Dictionary=harbor_adapter.configure(game,directory,environment_mode=="night",camera,view)
'''+anchor)
anchor="            (frozen/'preview.gd').write_text(preview);run.bind(frozen/'preview.gd')"
addition='''            preview=preview.replace('\\t\\t_:assert(false)','\\t\\t"dock-front","dock-back","boat-close":pass\\n\\t\\t_:assert(false)')
            preview=preview.replace('report["environment_study"]=environment_report','report["environment_study"]=environment_report\\n\\treport["harbor_study"]=harbor_report')
'''
assert anchor in s;s=s.replace(anchor,addition+anchor)
start=s.index('            views=');end=s.index('\n            for name,view,mode',start)
s=s[:start]+"            views=[('day-reference','reference-coast-near','day'),('night-reference','reference-coast-near','night'),('dock-front','dock-front','day'),('dock-back','dock-back','day'),('boat-close','boat-close','day'),('night-dock','dock-front','night')]"+s[end:]
s=s.replace("require(env['ambient_source']==2 and len(env['local_light_records'])==4,'Color ambient or lamp records missing')","if mode=='night':require(env['ambient_source']==2 and len(env['local_light_records'])==4,'Color ambient or lamp records missing')\n                harbor=data['harbor_study']\n                require(len(harbor['house_footings'])==23 and len(harbor['pier_entries'])==4 and len(harbor['lights'])==39,'Incomplete harbor assembly')\n                require(all(point['gap_m']<0 for house in harbor['house_footings'] for point in house['samples']),'Positive sampled harbor foundation gap')")
s=s.replace("print('COAST ENVIRONMENT STUDY READY '","print('HARBOR ASSEMBLY STUDY READY '")
p.write_text(s,encoding='utf-8');print(p)
