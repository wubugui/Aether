from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=(root/'blender/model_harbor_paths_22d.py').read_text(encoding='utf-8').replace('22d','22e')
old="top=max(top,end_height-.12*max(0.,length-rows[group[-1]+1]['distance_m']))"
new="if rows[group[-1]+1]['distance_m']>length-4.:top=max(top,end_height-.12*max(0.,length-rows[group[-1]+1]['distance_m']))"
assert source.count(old)==1;source=source.replace(old,new)
target=root/'blender/model_harbor_paths_22e.py';assert not target.exists();target.write_text(source,encoding='utf-8')
for name in ['harbor_assembly','harbor_path_runtime']:
    source=(root/('captures/'+name+'_22d.gd')).read_text(encoding='utf-8').replace('22d','22e')
    target=root/('captures/'+name+'_22e.gd');assert not target.exists();target.write_text(source,encoding='utf-8')
source=(root/'captures/check_harbor_kit_22.py').read_text(encoding='utf-8').replace('harbor_kit_study_','harbor_paths_study_').replace("'-harbor-native-check.json'","'-harbor-paths-native-check.json'")
target=root/'captures/check_harbor_paths_22.py';assert not target.exists();target.write_text(source,encoding='utf-8')
