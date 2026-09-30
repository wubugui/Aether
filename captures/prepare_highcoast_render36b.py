from pathlib import Path
R=Path(__file__).resolve().parents[1]
out=R/'tools/render_highcoast_36b.py'
assert not out.exists()
s=(R/'tools/render_highcoast_36a.py').read_text(encoding='utf-8').replace('36a','36b')
s=s.replace("names=['storm-high'", "names=['alongshore-high','alongshore-low','storm-high'")
s=s.replace("'fixed_views':7", "'fixed_views':9")
s=s.replace("same-world10GPU frames", "same-world12GPU frames")
s=s.replace("shutil.copy2(__file__,local/Path(__file__).name)", """shutil.copy2(__file__,local/Path(__file__).name)
            for extra in ['save_highcoast_candidate_36b.gd','candidate_game_36b.gd']:
                shutil.copy2(root/'tools'/extra,local/extra)""")
s=s.replace('''\\tvar views:Array=[
''','''\\tvar candidate_saver=load(directory.path_join("highcoast36b/save_highcoast_candidate_36b.gd")).new()
\\tvar candidate_report:Dictionary=candidate_saver.save_candidate(game,directory.path_join("highcoast36b"),output.get_base_dir())
\\tvar views:Array=[
\\t\\t["alongshore-high",Vector3(-2250,250,-1870),Vector3(-3040,120,-3580),65.,0.],
\\t\\t["alongshore-low",Vector3(-2400,100,-2310),Vector3(-3300,90,-3990),65.,2.05],
''')
s=s.replace('Vector3(-3100,0,-3190).lerp(Vector3(-1700,0,-3310),t)', 'Vector3(-3100,0,-3190).lerp(Vector3(-1390,0,-3210),t)')
s=s.replace('''\\t\\tp.y=actual_height+50.;camera.position=p;camera.look_at(p+Vector3(140,-20,-12));camera.fov=70.''', '''\\t\\tvar direction:=Vector3(1710,0,-20).normalized()
\\t\\tvar ahead_max:float=actual_height
\\t\\tfor advance in range(0,241,20):ahead_max=maxf(ahead_max,game.get_node("World").terrain_height(p+direction*float(advance)))
\\t\\tp.y=ahead_max+65.;camera.position=p;camera.look_at(p+direction*180.+Vector3(0,-15,0));camera.fov=70.''')
s=s.replace('"clearance":p.y-actual_height}', '"clearance":p.y-actual_height,"ahead_240m_max_mesh_height":ahead_max}')
s=s.replace('following new saved mesh height', 'following 240m forward terrain envelope')
s=s.replace('new mesh height+50m', 'new 240m forward mesh envelope+65m')
s=s.replace("actual['scatter_total_preserved']==54800", "actual['scatter_total_preserved']==54800")
s=s.replace("all(abs(p['clearance']-50)<.002 for p in flight['samples'])", "all(p['clearance']>=64.999 for p in flight['samples'])")
s=s.replace("final.parent/'flight-traverse.json']", "final.parent/'flight-traverse.json',final.parent/'candidate-scenes.json']")
s=s.replace("flight_samples=65,views=names", "flight_samples=65,candidate_scenes=read_json(final.parent/'candidate-scenes.json'),views=names")
out.write_text(s,encoding='utf-8')
print(out)
