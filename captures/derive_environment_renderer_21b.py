from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=root/'tools/render_coast_environment_21b.py';assert not p.exists()
s=(root/'tools/render_coast_environment_21a.py').read_text().replace('21a','21b')
anchor='            for path in [gate,Path(__file__)'
at=s.index(anchor)
insert='''            sky_source=root/'captures/coastal_sky_assets_21b'
            sky_gate=root/'reviews/round-21b-sky-native-check.json'
            require(read_json(sky_gate)['passed'],'Sky native gate failed')
            sky_frozen=environment/'sky-assets';sky_frozen.mkdir()
            for path in sky_source.iterdir():
                if path.is_file():shutil.copy2(path,sky_frozen/path.name);run.bind(sky_frozen/path.name)
            shutil.copy2(sky_gate,sky_frozen/sky_gate.name);run.bind(sky_frozen/sky_gate.name)
            for item in read_json(sky_gate)['assets']:
                require(sha256(sky_frozen/(item['asset']+'.blend'))==item['source_sha256'] and sha256(sky_frozen/(item['asset']+'.glb'))==item['glb_sha256'],'Sky source/export identity changed')
'''
s=s[:at]+insert+s[at:]
s=s.replace("[('day-paths','paths','day'),('day-reference'","[('day-reference'")
s=s.replace("Day paths and reference view, same reference at night and a reverse night view.","Native Blender lunar sphere/cloud banks, brighter actual night fill and crossed wave reflection. Day reference, night reference and reverse night views.")
s=s.replace("require(env['night']==(mode=='night') and len(env['material_bindings'])>=5,'Environment not applied')","require(env['night']==(mode=='night') and len(env['material_bindings'])>=5,'Environment not applied')\n                require(len(env['native_sky_assets'])==(8 if mode=='night' else 7),'Native sky geometry missing')")
p.write_text(s);print(p)
