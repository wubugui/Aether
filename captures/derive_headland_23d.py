from pathlib import Path
root=Path(__file__).resolve().parents[1]
base=(root/'blender/model_harbor_paths_22f.py').read_text(encoding='utf-8').split('# Appended to the standalone')[0]
base=base.replace("OUT=ROOT/'captures/harbor_paths_study_22f'","OUT=ROOT/'captures/headland_study_23d'")
wall=(root/'blender/model_lantern_islands_20h.py').read_text(encoding='utf-8').split('def wall(',1)[1].split("wall('Keeper front'",1)[0]
target=root/'blender/model_headland_23d.py'
assert not target.exists()
target.write_text(base+'\n'+(root/'captures/headland_23d_body.py').read_text(encoding='utf-8')+'\n'+'def wall('+wall+'\n'+(root/'captures/headland_houses_23d_body.py').read_text(encoding='utf-8'),encoding='utf-8')
